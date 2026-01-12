# Schedule Extraction Workflow: Web Developer Guide

## Overview

This document describes the unified workflow for financial and schedule extraction, focusing on how the web application interacts with the extraction pipeline through the `sch.p6_extraction_submissions` PostgreSQL table. The workflow enables users to request schedule extractions through the frontend, which triggers the extraction pipeline and provides version tracking and reconciliation capabilities.

---

## High-Level Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE EXTRACTION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────┘

1. FINANCIAL EXTRACTION (Script 01)
   ├── Extracts financial data from Snowflake
   ├── Updates: metadata_extract_status = 2
   └── Prerequisite for schedule extraction

2. USER REQUEST (Web Frontend)
   ├── User clicks "Request Extraction" or selects schedule
   ├── Backend creates/updates submission record
   └── submission_status = 0 (pending)

3. SCHEDULE EXTRACTION (Script 02)
   ├── Worker picks up pending submissions
   ├── Extracts from Primavera P6 API
   ├── Compares with previous versions (reconciliation)
   ├── Creates new version if schedule changed
   └── Updates: submission_status = 2, version_id, schedule_change

4. FRONTEND DISPLAY
   ├── Shows extraction status and statistics
   ├── Displays version history
   └── Enables comparison/reconciliation with previous extracts
```

---

## Database Schema: Key Tables

### `sch.p6_extraction_submissions` (Source of Truth)

**Primary Table** - Tracks all extraction requests and their status.

```sql
Key Fields:
- id (PK, auto-increment)
- job_code (project number)
- schedule_shortname
- submitted_fiscal_year_month_no (YYYYMM format)
- schedule_type (current_baseline, current_period, prior_period)
- submission_status (0=pending, 1=extracting, 2=complete, 9=error)
- metadata_extract_status (0=incomplete, 2=financial complete)
- version_id (FK to p6_schedule_id_versions.version_id)
- schedule_change (boolean: true if schedule changed, false if unchanged)
- user_extraction_requested (boolean: true if user manually requested)
- schedule_id (P6 ObjectId, varchar)
- database_instance_id (P6 database instance)
- created_at, updated_at (timestamps)
```

**Status Codes:**
- `0` = Pending (ready for extraction)
- `1` = Extracting (worker is processing)
- `2` = Extraction Complete
- `3` = Aggregating (next pipeline stage)
- `4` = Aggregation Complete
- `5` = Loading to Iceberg
- `6` = Complete (all stages done)
- `9` = Error

### `sch.p6_schedule_id_versions` (Version Tracking)

**Tracks all versions of extracted schedules** - enables reconciliation.

```sql
Key Fields:
- version_id (PK, auto-increment)
- submission_id (FK to p6_extraction_submissions.id)
- schedule_id (P6 ObjectId, varchar)
- version_number (1, 2, 3... per schedule_id + database_instance_id)
- output_dir_url (file location: "bronze/p6/V3/job_code=XX/sch_id=YY/version")
- service_activity_file_hash (SHA256 hash)
- service_calendar_file_hash
- service_resource_file_hash
- service_spread_file_hash
- service_relationship_file_hash
- service_*_row_count, service_*_col_count (metadata)
```

**Version Numbering:**
- Versions are scoped per `(schedule_id, database_instance_id)`
- Each time a schedule changes, version_number increments: 1, 2, 3...
- File hashes are compared to detect changes (SHA256 of parquet files)

### `sch.p6_extraction_logs` (Extraction Statistics)

**Tracks extraction performance and errors** - provides statistics for frontend.

```sql
Key Fields:
- id (PK)
- submission_id (FK to p6_extraction_submissions.id)
- started_at, completed_at, duration_seconds
- service_activity_duration_in_ms
- service_calendar_duration_in_ms
- service_resource_duration_in_ms
- service_spread_duration_in_ms
- service_relationship_duration_in_ms
- metadata_duration_in_ms
- is_error, error_message, error_service
- is_last (boolean: true for most recent log per submission)
```

---

## Workflow Details

### Step 1: Financial Extraction (Prerequisite)

**Script:** `01_jsr_inc_fin_extraction.py`

**Process:**
1. Extracts financial data from Snowflake (Cost Report, JOR, CRM)
2. Writes to Azure Blob: `bronze/jsr_financials/V3/fiscal_year_month_no=YYYYMM/project_number=XXX/data.parquet`
3. Updates PostgreSQL:
   ```sql
   UPDATE sch.p6_extraction_submissions
   SET metadata_extract_status = 2,
       financial_snapshot_at = NOW()
   WHERE job_code = <project_number>
   ```

**Key Point:** Schedule extraction **cannot proceed** until `metadata_extract_status = 2`.

---

### Step 2: User Requests Schedule Extraction (Web Frontend)

**How the Frontend Triggers Extraction:**

When a user wants to extract or re-extract a schedule, the web application should:

1. **Create or Update Submission Record:**
   ```python
   from backend.p6_extraction_submissions import create_submission
   
   submission_id = create_submission(
       job_code="103440",
       schedule_shortname="E130C-CBSL Rev B (MHR)",
       submitted_fiscal_year_month_no="202512",
       schedule_type="current_baseline",  # or "current_period", "prior_period"
       submission_status=0,  # 0 = pending (ready for worker to pick up)
       user_extraction_requested=True,  # User manually requested
       metadata_extract_status=None,  # Will be set by financial extraction
       record_origin="web"  # or "jsr" for automated
   )
   ```

2. **Or Update Existing Record:**
   ```python
   from backend.p6_extraction_submissions import update_submission_status_by_keys
   
   # Reset status to pending to trigger re-extraction
   update_submission_status_by_keys(
       job_code="103440",
       schedule_shortname="E130C-CBSL Rev B (MHR)",
       submitted_fiscal_year_month_no="202512",
       submission_status=0,  # Reset to pending
       user_extraction_requested=True
   )
   ```

**Important:** Set `submission_status = 0` to signal the worker to process this submission.

---

### Step 3: Schedule Extraction (Automated Worker)

**Script:** `02_sch_extraction.py`

**Process Flow:**

```
INPUT: job_code, schedule_shortname, fiscal_month

STEP 0: Atomic Lock
├── Uses SELECT FOR UPDATE SKIP LOCKED
├── Only locks records with submission_status = 0
├── Sets submission_status = 1 (processing)
└── Prevents race conditions with parallel workers

STEP 0a: Validate Prerequisites
├── Checks metadata_extract_status = 2 (financial complete)
└── If fail → unlock (status=9) and exit

STEP 1: Lookup schedule_id and database_instance_id
├── First checks p6_extraction_submissions table
└── Falls back to p6_schedule_id_cache if NULL

STEP 2: Extract P6 Services (in order)
├── ActivityService
├── CalendarService
├── ResourceAssignmentService
├── ResourceAssignmentSpreadService
└── RelationshipService

STEP 3: Calculate File Hashes (in memory)
├── Convert DataFrame to parquet bytes
├── Calculate SHA256 hash for each service
└── Store hashes (don't write files yet)

STEP 4: RECONCILIATION - Compare with Previous Versions
├── Query p6_schedule_id_versions for latest version
├── Compare file hashes for each service
└── If ANY hash differs → new version needed

STEP 5: Write Files and Create Version (if needed)
├── If changes detected:
│   ├── Calculate next version_number (increment by 1)
│   ├── Write parquet files to blob storage
│   │   Path: bronze/p6/V3/job_code=XX/sch_id=YY/{version}/{service}.parquet
│   ├── Create record in p6_schedule_id_versions
│   └── Update p6_extraction_submissions:
│       ├── version_id = <new version_id>
│       ├── schedule_change = true
│       └── submission_status = 2 (complete)
└── If NO changes:
    ├── Skip file write (files unchanged, saves storage)
    ├── Use existing version_id
    ├── schedule_change = false
    └── submission_status = 2 (complete)

STEP 6: Write Extraction Logs
├── Creates record in p6_extraction_logs
├── Records timing statistics per service
├── Sets is_last = true
└── Includes error information if failed
```

**Key Reconciliation Logic:**

The reconciliation process compares the **current extraction** with the **latest previous version**:

1. **Hash Comparison:** Each service's parquet file is hashed (SHA256) and compared with the previous version's hash
2. **Change Detection:** If ANY service hash differs, a new version is created
3. **Storage Efficiency:** If all hashes match, files are NOT written (unchanged data)
4. **Version Linking:** The `version_id` FK links submissions to their version records

**Example Reconciliation Scenario:**

```
Previous Extraction (version 2):
- activity.hash = "abc123"
- calendar.hash = "def456"
- resource.hash = "ghi789"

Current Extraction:
- activity.hash = "abc123"  (unchanged)
- calendar.hash = "def456"  (unchanged)
- resource.hash = "xyz999"  (CHANGED!)

Result: New version created (version 3)
- schedule_change = true
- Files written for version 3
- version_id updated in submissions table
```

---

## Frontend Integration

### Displaying Submission Status

The frontend can query the API to display submission status:

```typescript
// GET /api/schedules?fiscal_month=202512
interface ScheduleSubmission {
  id: number
  project_number: string
  schedule_type: string
  schedule_shortname: string
  status: number  // 0-9 status codes
  status_name: string  // "pending", "extracting", "complete", etc.
  version_id: number | null  // FK to versions table
  schedule_change: boolean | null  // true if schedule changed
  financial_snapshot_complete: number | null  // 1 if financial complete
  timestamp: string | null
  error_message: string | null
}
```

### Requesting Extraction (User Action)

When user clicks "Extract Schedule" or "Re-extract":

```typescript
// POST /api/submissions (new endpoint needed)
// OR use backend function directly
async function requestExtraction(
  jobCode: string,
  scheduleShortname: string,
  fiscalMonth: string,
  scheduleType: string
) {
  // Create submission with status=0 (pending)
  const response = await fetch('/api/submissions', {
    method: 'POST',
    body: JSON.stringify({
      job_code: jobCode,
      schedule_shortname: scheduleShortname,
      submitted_fiscal_year_month_no: fiscalMonth,
      schedule_type: scheduleType,
      submission_status: 0,  // Pending - worker will pick up
      user_extraction_requested: true
    })
  })
}
```

### Displaying Version History and Statistics

To show version history and statistics:

```typescript
// Get submission details (includes version_id)
const submission = await fetch(`/api/schedules/${projectNumber}?fiscal_month=${fiscalMonth}`)

// Get version details (includes file hashes, row counts, output_dir_url)
const version = await fetch(`/api/versions/${submission.version_id}`)

// Get extraction statistics (timing, errors)
const stats = await fetch(`/api/stats/extract?submission_id=${submission.id}`)
```

**Version Information Available:**
- `version_number` (1, 2, 3...)
- `output_dir_url` (file location for this version)
- File hashes for each service (for comparison)
- Row/column counts (metadata)
- Timestamp when version was created

**Extraction Statistics Available:**
- Total duration (`duration_seconds`)
- Per-service durations (`service_activity_duration_in_ms`, etc.)
- Error information (`is_error`, `error_message`, `error_service`)
- Start/completion timestamps

---

## Reconciliation in Visualizer

### Context: Comparing Previous Extracts

The visualizer enhancement will reconcile current schedule data with previous extracts. Here's how it works:

1. **Version Tracking:**
   - Each extraction creates a version record in `p6_schedule_id_versions`
   - Versions are linked via `version_id` FK in submissions table
   - File hashes enable change detection

2. **Reconciliation Process:**
   ```python
   # Pseudo-code for reconciliation
   current_version = get_version(submission.version_id)
   previous_versions = get_all_versions(schedule_id, database_instance_id)
   
   for prev_version in previous_versions:
       compare_file_hashes(current_version, prev_version)
       if hashes_differ:
           # Show differences in visualizer
           highlight_changes(service, prev_version.version_number)
   ```

3. **File Location for Reading Previous Versions:**
   ```python
   # Version record contains output_dir_url
   output_dir_url = "bronze/p6/V3/job_code=103440/sch_id=123456/2"
   
   # Files are at:
   # {output_dir_url}/activity.parquet
   # {output_dir_url}/calendar.parquet
   # {output_dir_url}/resource.parquet
   # {output_dir_url}/spread.parquet
   # {output_dir_url}/relationship.parquet
   ```

4. **What the Visualizer Can Display:**
   - **Version History:** List all versions (1, 2, 3...) for a schedule
   - **Change Indicators:** Show which services changed between versions
   - **Comparison View:** Compare current version with previous version
   - **Statistics:** Show extraction timing and metadata for each version
   - **File Locations:** Direct links to parquet files for each version

---

## Summary: Key Points for Web Developer

1. **Creating Submissions:**
   - Use `create_submission()` from `backend.p6_extraction_submissions`
   - Set `submission_status = 0` to trigger extraction
   - Set `user_extraction_requested = True` if user manually requested

2. **Status Flow:**
   ```
   0 (pending) → 1 (extracting) → 2 (complete) → 3 (aggregating) → 4 → 5 → 6
                                                                    ↓
                                                                  9 (error)
   ```

3. **Prerequisites:**
   - Financial extraction must complete first (`metadata_extract_status = 2`)
   - Schedule extraction will fail if financial data not ready

4. **Version Tracking:**
   - Each extraction creates a version if schedule changed
   - Versions are tracked per `(schedule_id, database_instance_id)`
   - File hashes enable change detection and reconciliation

5. **Reconciliation:**
   - Compare current extraction with previous versions using file hashes
   - Access previous versions via `p6_schedule_id_versions` table
   - File locations stored in `output_dir_url` field

6. **Frontend Display:**
   - Query `/api/schedules` for submission status
   - Query `/api/stats/extract?submission_id=X` for statistics
   - Query version information via `version_id` FK
   - Use `schedule_change` flag to indicate if schedule was modified

---

## API Endpoints Needed (Recommended)

```typescript
// Create/Request extraction
POST /api/submissions
  Body: { job_code, schedule_shortname, submitted_fiscal_year_month_no, schedule_type }
  Creates submission with status=0 (pending)

// Get version details
GET /api/versions/{version_id}
  Returns version information including file hashes, output_dir_url, metadata

// Get version history for a schedule
GET /api/versions?schedule_id={schedule_id}&database_instance_id={db_id}
  Returns all versions for a schedule (for reconciliation)

// Get extraction statistics
GET /api/stats/extract?submission_id={submission_id}
  Returns timing, errors, per-service statistics
```

---

## Example: Complete User Flow

1. **User Views Dashboard:**
   - Frontend queries `/api/schedules?fiscal_month=202512`
   - Shows list of schedules with status indicators

2. **User Requests Extraction:**
   - User clicks "Extract" button for a schedule
   - Frontend calls `POST /api/submissions` (or backend function)
   - Creates record with `submission_status = 0`, `user_extraction_requested = true`

3. **Worker Processes:**
   - Worker picks up pending submission
   - Extracts from P6 API
   - Compares with previous version (reconciliation)
   - Creates new version if changed
   - Updates `submission_status = 2`, `version_id`, `schedule_change`

4. **User Views Results:**
   - Frontend refreshes, shows status = "Complete"
   - Displays version number and statistics
   - Shows `schedule_change = true/false` indicator
   - Visualizer can now reconcile with previous versions using `version_id`

---

## File References

- **Financial Extraction:** `scripts/01_jsr_inc_fin_extraction.py`
- **Schedule Extraction:** `scripts/02_sch_extraction.py`
- **Backend Functions:** `backend/p6_extraction_submissions.py`
- **Version Tracking:** `backend/p6_schedule_id_versions.py`
- **Extraction Logs:** `backend/p6_extraction_logs.py`
