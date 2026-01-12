# Status Codes: Pipeline Status Tracking

This document explains the status tracking system used in the JSR extraction pipeline, including `metadata_extract_status` (for financial extraction) and `submission_status` (for the overall pipeline stages: JOR P6 extraction, schedule publisher, aggregation, and Iceberg write).

---

## Two Status Systems

The pipeline uses **two separate but related status fields**:

1. **`metadata_extract_status`** - Tracks financial extraction completion (prerequisite)
2. **`submission_status`** - Tracks the main pipeline stages (0-6, plus error codes)

---

## Status Field 1: `metadata_extract_status` (Financial Extraction)

**Purpose:** Tracks whether financial data has been extracted from Snowflake (Cost Report, JOR, CRM).

**Field:** `metadata_extract_status` (INT4, nullable)

**Values:**
- `NULL` or `0` = Financial extraction incomplete/not started
- `2` = Financial extraction complete ✅

**Set By:** `01_jsr_inc_fin_extraction.py` (financial extraction script)

**Usage:**
- **Prerequisite Check:** Schedule extraction (`02_sch_extraction.py`) requires `metadata_extract_status = 2` before proceeding
- **Frontend Display:** Mapped to `financial_snapshot_complete` field (1 if metadata_extract_status=2, otherwise NULL/0)

**Example:**
```sql
-- After financial extraction completes
UPDATE sch.p6_extraction_submissions
SET metadata_extract_status = 2,
    financial_snapshot_at = NOW()
WHERE job_code = '103440'
  AND submitted_fiscal_year_month_no = '202512'
```

**Key Point:** This is a **binary state** (incomplete vs. complete), not a multi-stage progression like `submission_status`.

---

## Status Field 2: `submission_status` (Main Pipeline)

**Purpose:** Tracks the progression through the main extraction pipeline stages (P6 extraction, aggregation, Iceberg write).

**Field:** `submission_status` (INT2, default 0)

**Status Code Values (0-6):**

### Status 0: Pending / Not Run
- **Name:** "Not Run" (backend), "Pending" (frontend)
- **Meaning:** Submission is ready to be processed, waiting for a worker
- **When Set:** Initial state when submission record is created
- **Next:** Worker picks up and transitions to status 1

### Status 1: Extracting (P6 Extraction)
- **Name:** "Extracting"
- **Meaning:** P6 extraction is currently in progress
- **Script:** `02_sch_extraction.py` (Schedule Extraction)
- **When Set:** Atomic lock at start of P6 extraction (prevents race conditions)
- **Visual:** **Animated** in frontend (blue pulsing indicator)
- **Next:** Completes → status 2, or errors → status 9

### Status 2: Extraction Complete
- **Name:** "Extracted"
- **Meaning:** P6 extraction has completed successfully
- **Script:** `02_sch_extraction.py` sets this after extraction completes
- **What Happened:** 
  - Schedule data extracted from Primavera P6 API
  - Files written to blob storage (if schedule changed)
  - Version record created in `p6_schedule_id_versions`
- **Next:** Aggregation can begin → status 3

### Status 3: Aggregating
- **Name:** "Aggregating"
- **Meaning:** Aggregation process is currently running (combining P6 + Financial data)
- **Script:** `03_jsr_aggregation.py` (Parquet Aggregation)
- **When Set:** Locked when aggregation starts
- **Visual:** **Animated** in frontend (blue pulsing indicator)
- **Next:** Completes → status 4, or errors → status 9

### Status 4: Aggregation Complete
- **Name:** "Aggregated"
- **Meaning:** Aggregation has completed successfully
- **Script:** `03_jsr_aggregation.py` sets this after aggregation completes
- **What Happened:**
  - Financial data + P6 schedule data combined
  - Silver layer parquet files written to blob storage
- **Next:** Iceberg write can begin → status 5

### Status 5: Writing Iceberg / Loading Iceberg
- **Name:** "Writing Iceberg"
- **Meaning:** Data is being loaded to Iceberg tables (analytics layer)
- **Script:** `04_jsr_iceberg_write.py` (Iceberg Write)
- **When Set:** Locked when Iceberg load starts
- **Visual:** **Animated** in frontend (blue pulsing indicator)
- **Next:** Completes → status 6, or errors → status 9

### Status 6: Complete
- **Name:** "Complete"
- **Meaning:** All pipeline stages have completed successfully
- **Script:** `04_jsr_iceberg_write.py` sets this after Iceberg load completes
- **What Happened:**
  - Financial extraction ✅
  - P6 extraction ✅
  - Aggregation ✅
  - Iceberg write ✅
- **Final State:** Pipeline is done for this submission

### Status 9: Error
- **Name:** "Error"
- **Meaning:** An error occurred at any stage
- **When Set:** Any script can set this if an error occurs
- **Visual:** Error indicator in frontend (red/gray)
- **Error Details:** Stored in `p6_extraction_logs.error_message` and `error_service`

### Status -9: Invalid Data (Legacy)
- **Name:** "Invalid Data"
- **Meaning:** Legacy error code (may be used in some contexts)
- **Usage:** Similar to status 9 (error state)

---

## Status Flow Diagram

```
FINANCIAL EXTRACTION (Prerequisite)
────────────────────────────────────
metadata_extract_status: NULL/0 → 2 (complete)
                              ↓
                           Prerequisite
                              ↓
MAIN PIPELINE (submission_status)
────────────────────────────────────
Status 0: Pending
    ↓
Status 1: Extracting (P6) ⚡ [ANIMATED]
    ↓
Status 2: Extraction Complete
    ↓
Status 3: Aggregating ⚡ [ANIMATED]
    ↓
Status 4: Aggregation Complete
    ↓
Status 5: Writing Iceberg ⚡ [ANIMATED]
    ↓
Status 6: Complete ✅

Any stage → Status 9: Error ❌
```

---

## Pipeline Visualizer Mapping

Based on `frontend/components/pipeline-visualizer.tsx` and `schedule-dashboard.tsx`:

### Stage 1: Financial JSR
- **Field Used:** `financial_snapshot_complete` (derived from `metadata_extract_status`)
- **Mapping:** `financial_snapshot_complete = 1` if `metadata_extract_status = 2`, otherwise 0/NULL
- **Status:** Binary (complete or not complete)
- **Script:** `01_jsr_inc_fin_extraction.py`

### Stage 2: P6 Extraction
- **Field Used:** `submission_status`
- **Status Range:** `[0, 1, 2]`
  - 0 = Not started
  - 1 = In progress (extracting) ⚡
  - 2 = Complete
- **Script:** `02_sch_extraction.py`

### Stage 3: Parquet Aggregation
- **Field Used:** `submission_status`
- **Status Range:** `[2, 3, 4]`
  - < 3 = Not started
  - 3 = In progress (aggregating) ⚡
  - ≥ 4 = Complete
- **Script:** `03_jsr_aggregation.py`

### Stage 4: Iceberg Write
- **Field Used:** `submission_status`
- **Status Range:** `[4, 5, 6]`
  - < 5 = Not started
  - 5 = In progress (loading) ⚡
  - 6 = Complete
- **Script:** `04_jsr_iceberg_write.py`

---

## Status Code Pattern: Odd = In Progress, Even = Complete

**Key Pattern:**
- **Even numbers (0, 2, 4, 6):** Stable/complete states
- **Odd numbers (1, 3, 5):** In-progress states (animated in frontend)

This pattern allows the frontend to easily identify which stages are actively running:
- Status 1 = P6 extraction in progress
- Status 3 = Aggregation in progress
- Status 5 = Iceberg write in progress

---

## Frontend Status Display Logic

From `frontend/components/schedule-dashboard.tsx`:

```typescript
// Financial Stage
if (schedule.financial_snapshot_complete === 1) → "finished"
else → "not_started"

// Extraction Stage
if (status === 0) → "not_started"
if (status === 1) → "in_progress" (animated)
if (status === 2) → "finished"
if (status > 2) → "finished" (extraction is done)

// Aggregation Stage
if (status < 3) → "not_started"
if (status === 3) → "in_progress" (animated)
if (status >= 4) → "finished"

// Iceberg Stage
if (status < 5) → "not_started"
if (status === 5) → "in_progress" (animated)
if (status === 6) → "finished"
```

---

## Status Transitions in Code

### Financial Extraction (metadata_extract_status)
```python
# Script: 01_jsr_inc_fin_extraction.py
set_financial_snapshot_complete(job_code, fiscal_month)
# Sets: metadata_extract_status = 2
```

### P6 Extraction (submission_status 0 → 1 → 2)
```python
# Script: 02_sch_extraction.py
# Step 0: Lock (0 → 1)
lock_submission(...)  # Sets submission_status = 1

# Step 5: Complete (1 → 2)
update_submission_status_by_keys(..., submission_status=2)
```

### Aggregation (submission_status 2 → 3 → 4)
```python
# Script: 03_jsr_aggregation.py
# Lock for aggregation (2 → 3)
lock_for_aggregation(...)  # Sets submission_status = 3

# Complete aggregation (3 → 4)
complete_aggregation(...)  # Sets submission_status = 4
```

### Iceberg Write (submission_status 4 → 5 → 6)
```python
# Script: 04_jsr_iceberg_write.py
# Lock for iceberg (4 → 5)
lock_for_iceberg(...)  # Sets submission_status = 5

# Complete (5 → 6)
complete_iceberg(...)  # Sets submission_status = 6
```

---

## Usage in Schedule Publisher and Other Processes

The `submission_status` field is designed to be **reusable** for different extraction processes:

1. **JOR P6 Extraction** (current implementation)
   - Uses status 0-6 as described above
   - Tracks: P6 extraction → Aggregation → Iceberg

2. **Schedule Publisher** (future use)
   - Can use the same status codes (0-6)
   - Can track its own pipeline stages using the same numbering scheme
   - Status 0-2 could represent publisher-specific stages
   - Status 3-6 could represent aggregation/Iceberg stages

3. **Other Extraction Processes**
   - Same status code pattern applies
   - Even numbers = complete states
   - Odd numbers = in-progress states
   - Status 9 = error state

**Flexibility:** The status codes are generic enough to represent any multi-stage pipeline process, not just the current JOR P6 extraction flow.

---

## Status Name Mapping (Backend)

From `backend/main.py`:

```python
def _convert_status_name(status: int) -> str:
    status_map = {
        0: "Not Run",
        1: "Extracting",
        2: "Extracted",
        3: "Aggregating",
        4: "Aggregated",
        5: "Writing Iceberg",
        6: "Complete",
        9: "Error",
        -9: "Invalid Data",
    }
    return status_map.get(status, "Unknown")
```

---

## Summary Table

| Status Code | Name | Stage | Script | Visual State | Next Status |
|-------------|------|-------|--------|--------------|-------------|
| **metadata_extract_status** |
| NULL/0 | Incomplete | Financial | `01_jsr_inc_fin_extraction.py` | Not started | - |
| 2 | Complete | Financial | `01_jsr_inc_fin_extraction.py` | ✅ Complete | - |
| **submission_status** |
| 0 | Pending/Not Run | - | - | Not started | 1 |
| 1 | Extracting | P6 Extraction | `02_sch_extraction.py` | ⚡ In progress | 2 or 9 |
| 2 | Extracted | P6 Extraction | `02_sch_extraction.py` | ✅ Complete | 3 |
| 3 | Aggregating | Aggregation | `03_jsr_aggregation.py` | ⚡ In progress | 4 or 9 |
| 4 | Aggregated | Aggregation | `03_jsr_aggregation.py` | ✅ Complete | 5 |
| 5 | Writing Iceberg | Iceberg Write | `04_jsr_iceberg_write.py` | ⚡ In progress | 6 or 9 |
| 6 | Complete | All Stages | `04_jsr_iceberg_write.py` | ✅ Complete | - (final) |
| 9 | Error | Any Stage | Any script | ❌ Error | - |
| -9 | Invalid Data | Any Stage | Legacy | ❌ Error | - |

---

## Key Takeaways

1. **Two Status Fields:**
   - `metadata_extract_status` = Financial extraction (binary: incomplete/complete)
   - `submission_status` = Main pipeline stages (0-6 progression)

2. **Status Pattern:**
   - Even numbers (0, 2, 4, 6) = Stable/complete states
   - Odd numbers (1, 3, 5) = In-progress states (animated in UI)
   - 9 = Error state

3. **Prerequisite:**
   - `metadata_extract_status = 2` is required before `submission_status` can progress beyond 0

4. **Reusable:**
   - Status codes 0-6 can be used for Schedule Publisher and other extraction processes
   - The pattern is generic enough to represent any multi-stage pipeline
