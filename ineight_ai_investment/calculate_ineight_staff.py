#!/usr/bin/env python3
import pandas as pd

# Read the Excel file
df = pd.read_excel('employee_data_cumberland.xlsx')

# Filter to active assignments only
df_active = df[df['Assignment'] == 'ACTIVE'].copy()

print("=" * 80)
print("KIEWIT InEight USER ESTIMATION - CUMBERLAND PROJECT ANALYSIS")
print("=" * 80)

# Categorize based on job title and job family
def categorize_staff(row):
    job_title = str(row.get('HCM Job Title', '')).upper()
    job_family = str(row.get('HCM Job Family', '')).upper()
    
    # Field Engineer
    if 'FIELD ENGINEER' in job_title or 'FIELD ENGINEER' in job_family:
        return 'Field Engineer'
    
    # Project Engineer
    if 'PROJECT ENGINEER' in job_title or 'PROJECT ENGINEER' in job_family or job_family == 'PROJECT ENGINEERING':
        return 'Project Engineer'
    
    # Superintendent
    if 'SUPERINTENDENT' in job_title or job_family == 'FIELD SUPERVISION':
        return 'Superintendent'
    
    # Non-InEight User (everyone else)
    return 'Non-InEight User'

# Apply categorization
df_active['Category'] = df_active.apply(categorize_staff, axis=1)

# Count by category
category_counts = df_active['Category'].value_counts()
total_active = len(df_active)

# Calculate percentages
field_eng_count = category_counts.get('Field Engineer', 0)
project_eng_count = category_counts.get('Project Engineer', 0)
superintendent_count = category_counts.get('Superintendent', 0)
non_ineight_count = category_counts.get('Non-InEight User', 0)

total_ineight_users = field_eng_count + project_eng_count + superintendent_count
ineight_percentage = (total_ineight_users / total_active * 100) if total_active > 0 else 0

print(f"\nCUMBERLAND PROJECT BREAKDOWN:")
print(f"  Total Active Staff: {total_active}")
print(f"\n  Field Engineers: {field_eng_count} ({field_eng_count/total_active*100:.1f}%)")
print(f"  Project Engineers: {project_eng_count} ({project_eng_count/total_active*100:.1f}%)")
print(f"  Superintendents: {superintendent_count} ({superintendent_count/total_active*100:.1f}%)")
print(f"  Non-InEight Users: {non_ineight_count} ({non_ineight_count/total_active*100:.1f}%)")
print(f"\n  TOTAL InEight Users: {total_ineight_users} ({ineight_percentage:.1f}%)")

# Apply to Kiewit's total non-hourly staff
kiewit_total_non_hourly = 14946
kiewit_ineight_users_raw = int(kiewit_total_non_hourly * (ineight_percentage / 100))

# Remove 10% for overhead/non-execution roles (district office, estimating, management)
overhead_percentage = 10
kiewit_execution_staff = int(kiewit_total_non_hourly * (1 - overhead_percentage / 100))
kiewit_ineight_users_adjusted = int(kiewit_execution_staff * (ineight_percentage / 100))

print("\n" + "=" * 80)
print("KIEWIT ENTERPRISE ESTIMATION")
print("=" * 80)
print(f"\nTotal Non-Hourly Staff: {kiewit_total_non_hourly:,}")
print(f"  Less 10% Overhead/Non-Execution: {kiewit_total_non_hourly - kiewit_execution_staff:,}")
print(f"  Execution Staff: {kiewit_execution_staff:,}")

print(f"\nInEight Users (using Cumberland {ineight_percentage:.1f}% proxy):")
print(f"  Raw Calculation: {kiewit_ineight_users_raw:,} ({ineight_percentage:.1f}% of {kiewit_total_non_hourly:,})")
print(f"  Adjusted (execution only): {kiewit_ineight_users_adjusted:,} ({ineight_percentage:.1f}% of {kiewit_execution_staff:,})")

# Breakdown by role
field_eng_pct = (field_eng_count / total_active * 100) if total_active > 0 else 0
project_eng_pct = (project_eng_count / total_active * 100) if total_active > 0 else 0
superintendent_pct = (superintendent_count / total_active * 100) if total_active > 0 else 0

print("\n" + "=" * 80)
print("BREAKDOWN BY ROLE (Adjusted for Execution Staff Only)")
print("=" * 80)
print(f"\nField Engineers:")
print(f"  Cumberland: {field_eng_count} ({field_eng_pct:.1f}%)")
print(f"  Kiewit Estimate: {int(kiewit_execution_staff * field_eng_pct / 100):,}")

print(f"\nProject Engineers:")
print(f"  Cumberland: {project_eng_count} ({project_eng_pct:.1f}%)")
print(f"  Kiewit Estimate: {int(kiewit_execution_staff * project_eng_pct / 100):,}")

print(f"\nSuperintendents:")
print(f"  Cumberland: {superintendent_count} ({superintendent_pct:.1f}%)")
print(f"  Kiewit Estimate: {int(kiewit_execution_staff * superintendent_pct / 100):,}")

print(f"\nTOTAL InEight Users:")
print(f"  Cumberland: {total_ineight_users} ({ineight_percentage:.1f}%)")
print(f"  Kiewit Estimate: {kiewit_ineight_users_adjusted:,}")

# Example district calculation
print("\n" + "=" * 80)
print("EXAMPLE: DISTRICT OF 500 PEOPLE")
print("=" * 80)
district_total = 500
district_overhead = int(district_total * 0.10)
district_execution = district_total - district_overhead
district_ineight = int(district_execution * (ineight_percentage / 100))

print(f"\nTotal District Staff: {district_total}")
print(f"  District Office (10% overhead): {district_overhead}")
print(f"  Execution Staff: {district_execution}")
print(f"  InEight Users ({ineight_percentage:.1f}%): {district_ineight}")

# Save results
output_file = 'kiewit_ineight_staff_estimation.txt'
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("KIEWIT InEight USER ESTIMATION\n")
    f.write("Using Cumberland Project as Proxy\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("CUMBERLAND PROJECT BREAKDOWN:\n")
    f.write(f"  Total Active Staff: {total_active}\n")
    f.write(f"  Field Engineers: {field_eng_count} ({field_eng_pct:.1f}%)\n")
    f.write(f"  Project Engineers: {project_eng_count} ({project_eng_pct:.1f}%)\n")
    f.write(f"  Superintendents: {superintendent_count} ({superintendent_pct:.1f}%)\n")
    f.write(f"  TOTAL InEight Users: {total_ineight_users} ({ineight_percentage:.1f}%)\n\n")
    
    f.write("KIEWIT ENTERPRISE ESTIMATION:\n")
    f.write(f"  Total Non-Hourly Staff: {kiewit_total_non_hourly:,}\n")
    f.write(f"  Less 10% Overhead: {kiewit_total_non_hourly - kiewit_execution_staff:,}\n")
    f.write(f"  Execution Staff: {kiewit_execution_staff:,}\n\n")
    
    f.write("InEight Users (Execution Staff Only):\n")
    f.write(f"  Field Engineers: {int(kiewit_execution_staff * field_eng_pct / 100):,}\n")
    f.write(f"  Project Engineers: {int(kiewit_execution_staff * project_eng_pct / 100):,}\n")
    f.write(f"  Superintendents: {int(kiewit_execution_staff * superintendent_pct / 100):,}\n")
    f.write(f"  TOTAL: {kiewit_ineight_users_adjusted:,}\n")

print(f"\n\nResults saved to: {output_file}")


