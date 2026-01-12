# Frontend-Controlled Inputs: Submission Table Fields

This document summarizes the fields in `sch.p6_extraction_submissions` that the frontend/web application controls when creating or updating submission records.

---

## Overview

When a user requests a schedule extraction through the web frontend, the application creates or updates records in `sch.p6_extraction_submissions`. This document identifies which fields are set by the frontend vs. which are set automatically by the extraction pipeline.

---

## Frontend-Controlled Fields

### 1. User Extraction Request Flag

**Field:** `user_extraction_requested` (BOOLEAN)

**Purpose:** Indicates whether a user manually requested the extraction through the web interface.

**Frontend Control:**
- Set to `true` when user clicks "Extract Schedule" or "Re-extract"
- Set to `false` or `NULL` for automated extractions (not user-initiated)

**Default:** `true` (when column is added)

**Nullable:** Yes (NULL for migrated records from Azure)

**Example:**
```python
create_submission(
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    schedule_type="current_baseline",
    user_extraction_requested=True  # Frontend sets this
)
```

---

### 2. Record Origin

**Field:** `record_origin` (VARCHAR(50))

**Purpose:** Identifies the source/system that created the submission record.

**Frontend Control:**
- Set to `"web"` when created via web frontend
- Set to `"jsr"` for automated/Dagster-created records
- Other values possible (e.g., `"api"`, `"migration"`)

**Default:** `'jsr'` (when column is added)

**Nullable:** Yes

**Example:**
```python
create_submission(
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    schedule_type="current_baseline",
    record_origin="web"  # Frontend sets this to distinguish from automated
)
```

---

### 3. Schedule ID (Optional)

**Field:** `schedule_id` (VARCHAR(100), nullable)

**Purpose:** The Primavera P6 schedule ObjectId. Used to identify the specific schedule in P6.

**Frontend Control:**
- **Optional** - Frontend can provide if known
- If `NULL`, extraction script will look it up from `p6_schedule_id_cache`
- If still `NULL` after lookup, extraction will fail with status=9 (error)

**Nullable:** Yes

**Example:**
```python
create_submission(
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    schedule_type="current_baseline",
    schedule_id="123456789"  # Frontend provides if known, otherwise NULL
)
```

**Note:** If frontend doesn't know the schedule_id, leave it as `NULL` - the extraction script will resolve it.

---

### 4. Database Instance ID (Optional)

**Field:** `database_instance_id` (INT4, nullable)

**Purpose:** The P6 database instance ID. Identifies which P6 database contains the schedule.

**Frontend Control:**
- **Optional** - Frontend can provide if known
- If `NULL`, extraction script will look it up from `p6_schedule_id_cache` or `p6_extraction_submissions`
- If still `NULL` after lookup, extraction will fail with status=9 (error)

**Nullable:** Yes

**Example:**
```python
create_submission(
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    schedule_type="current_baseline",
    database_instance_id=7  # Frontend provides if known, otherwise NULL
)
```

**Note:** If frontend doesn't know the database_instance_id, leave it as `NULL` - the extraction script will resolve it.

---

### 5. Required Business Keys (Always Set by Frontend)

These fields are **required** and **always** set by the frontend when creating a submission:

#### `job_code` (VARCHAR(100), NOT NULL)
- Project number (e.g., "103440")

#### `schedule_shortname` (VARCHAR(255), NOT NULL)
- Schedule name (e.g., "E130C-CBSL Rev B (MHR)")

#### `submitted_fiscal_year_month_no` (VARCHAR(10), nullable but recommended)
- Fiscal month in YYYYMM format (e.g., "202512")

#### `schedule_type` (VARCHAR(50), nullable but recommended)
- One of: `"current_baseline"`, `"current_period"`, `"prior_period"`

---

## Pipeline-Controlled Fields (NOT Set by Frontend)

These fields are **automatically set** by the extraction pipeline and should **NOT** be set by the frontend:

### `submission_status` (INT2)
- Set by pipeline: `0` (pending) initially, then `1` (extracting), `2` (complete), etc.
- **Frontend should set to `0`** when creating a new submission to trigger processing
- Pipeline controls all status transitions

### `schedule_change` (BOOLEAN)
- **Set by extraction script** (`02_sch_extraction.py`) after comparing file hashes
- `true` = schedule changed (new version created)
- `false` = schedule unchanged (reused existing version)
- Frontend does NOT control this - it's the result of reconciliation logic

### `version_id` / `version_number` (INT4)
- **Set by extraction script** after creating version record
- Foreign key to `p6_schedule_id_versions.version_id`
- Frontend does NOT control this

### `metadata_extract_status` (INT4)
- **Set by financial extraction script** (`01_jsr_inc_fin_extraction.py`)
- `2` = financial extraction complete (prerequisite for schedule extraction)
- Frontend does NOT control this

### `financial_snapshot_at` (TIMESTAMPTZ)
- **Set by financial extraction script**
- Timestamp when financial data was extracted
- Frontend does NOT control this

### `created_at`, `updated_at` (TIMESTAMPTZ)
- **Set automatically by database** (default NOW())
- Frontend does NOT control this

---

## Submission Status Control

**Initial Status:** Frontend should set `submission_status = 0` (pending) when creating a new submission.

**Status Flow (controlled by pipeline):**
```
0 (pending) → 1 (extracting) → 2 (complete) → 3 (aggregating) → 4 → 5 → 6
                                                                    ↓
                                                                  9 (error)
```

**To Request Re-extraction:**
Frontend can reset status to `0` (pending) to trigger re-processing:
```python
update_submission_status_by_keys(
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    submission_status=0,  # Reset to pending
    user_extraction_requested=True  # Mark as user-requested
)
```

---

## Complete Field Summary

| Field | Frontend Controls? | Type | Default | Notes |
|-------|-------------------|------|---------|-------|
| `id` | ❌ No | INT8 | Auto-increment | Primary key |
| `job_code` | ✅ **Yes** (Required) | VARCHAR(100) | - | Project number |
| `schedule_shortname` | ✅ **Yes** (Required) | VARCHAR(255) | - | Schedule name |
| `submitted_fiscal_year_month_no` | ✅ **Yes** | VARCHAR(10) | NULL | YYYYMM format |
| `schedule_type` | ✅ **Yes** | VARCHAR(50) | NULL | current_baseline, current_period, prior_period |
| `submission_status` | ✅ **Partial** (Set to 0) | INT2 | 0 | Pipeline controls transitions |
| `financial_snapshot_at` | ❌ No | TIMESTAMPTZ | NULL | Set by financial extraction |
| `record_origin` | ✅ **Yes** | VARCHAR(50) | 'jsr' | Set to "web" for frontend |
| `created_at` | ❌ No | TIMESTAMPTZ | NOW() | Auto-set by database |
| `updated_at` | ❌ No | TIMESTAMPTZ | NOW() | Auto-set by database |
| `schedule_id` | ✅ **Yes** (Optional) | VARCHAR(100) | NULL | P6 ObjectId, can be looked up |
| `version_number` / `version_id` | ❌ No | INT4 | NULL | Set by extraction script (FK) |
| `submitted_fiscal_month_week_no` | ❌ No | INT4 | NULL | Set by pipeline |
| `schedule_change` | ❌ No | BOOLEAN | false | Set by extraction script (reconciliation result) |
| `database_instance_id` | ✅ **Yes** (Optional) | INT4 | NULL | P6 database instance, can be looked up |
| `metadata_extract_status` | ❌ No | INT4 | NULL | Set by financial extraction (2 = complete) |
| `dagster_run_id` | ❌ No | VARCHAR(255) | NULL | Set by Dagster workflow |
| `user_extraction_requested` | ✅ **Yes** | BOOLEAN | true | Set to true for user requests |

---

## Frontend Submission Creation Example

```python
from backend.p6_extraction_submissions import create_submission

# User clicks "Extract Schedule" button in frontend
submission_id = create_submission(
    # Required fields (always set by frontend)
    job_code="103440",
    schedule_shortname="E130C-CBSL Rev B (MHR)",
    submitted_fiscal_year_month_no="202512",
    schedule_type="current_baseline",
    
    # Frontend-controlled fields
    submission_status=0,  # Set to 0 to trigger extraction
    user_extraction_requested=True,  # User manually requested
    record_origin="web",  # Distinguish from automated
    
    # Optional fields (frontend can provide if known)
    schedule_id="123456789",  # Or NULL if unknown (will be looked up)
    database_instance_id=7,  # Or NULL if unknown (will be looked up)
    
    # Pipeline-controlled fields (do NOT set)
    # version_number=None,  # Will be set by extraction script
    # schedule_change=None,  # Will be set by extraction script
    # metadata_extract_status=None,  # Will be set by financial extraction
)
```

---

## Key Takeaways

1. **Frontend Controls:**
   - User request flag (`user_extraction_requested`)
   - Record origin (`record_origin` = "web")
   - Optional: `schedule_id` and `database_instance_id` (if known)
   - Initial status (`submission_status = 0` to trigger)

2. **Pipeline Controls:**
   - Status transitions (1, 2, 3, 4, 5, 6, 9)
   - `schedule_change` (result of reconciliation)
   - `version_id` (created after extraction)
   - `metadata_extract_status` (set by financial extraction)

3. **Reconciliation:**
   - `schedule_change` is the **output** of reconciliation (not input)
   - Frontend cannot control whether a schedule changed
   - Extraction script compares file hashes to determine if change occurred
