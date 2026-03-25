#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
import numpy as np

print("=" * 80)
print("COMPREHENSIVE CUMBERLAND PROJECT ANALYSIS")
print("=" * 80)

# Step 1: Read and analyze employee data
print("\n" + "=" * 80)
print("STEP 1: LOADING EMPLOYEE DATA")
print("=" * 80)

df1 = pd.read_excel('employee_data_cumberland.xlsx')
print(f"Loaded {len(df1)} records from employee_data_cumberland.xlsx")

# Check for start date column
print(f"\nColumns: {df1.columns.tolist()}")

# Filter to active
df_active = df1[df1['Assignment'] == 'ACTIVE'].copy()
print(f"Active assignments: {len(df_active)}")

# Calculate days if we have start/end dates
if 'End Date' in df_active.columns:
    # Try to find start date - might be project start or assignment start
    # For now, we'll use End Date as reference point
    df_active['End Date'] = pd.to_datetime(df_active['End Date'], errors='coerce')
    print(f"\nDate range: {df_active['End Date'].min()} to {df_active['End Date'].max()}")

# Step 2: Enhanced categorization with 50 title sample
print("\n" + "=" * 80)
print("STEP 2: JOB TITLE CATEGORIZATION")
print("=" * 80)

def categorize_staff_enhanced(row):
    """Enhanced categorization - errs on side of binning into InEight categories"""
    job_title = str(row.get('HCM Job Title', '')).upper()
    job_family = str(row.get('HCM Job Family', '')).upper()
    
    # Field Engineer - be inclusive
    if any(term in job_title for term in ['FIELD ENGINEER', 'FIELD ENG', 'FE ']):
        return 'Field Engineer'
    if 'FIELD OPERATIONS' in job_family or 'FIELD ENGINEER' in job_family:
        return 'Field Engineer'
    
    # Project Engineer - be inclusive
    if any(term in job_title for term in ['PROJECT ENGINEER', 'PROJECT ENG', 'PE ', 'PROJ ENG']):
        return 'Project Engineer'
    if 'PROJECT ENGINEERING' in job_family or 'PROJECT ENGINEER' in job_family:
        return 'Project Engineer'
    
    # Superintendent - be inclusive
    if any(term in job_title for term in ['SUPERINTENDENT', 'SUPT', 'SUPER']):
        return 'Superintendent'
    if 'FIELD SUPERVISION' in job_family or 'SUPERINTENDENT' in job_family:
        return 'Superintendent'
    
    # Non-InEight User
    return 'Non-InEight User'

df_active['Category'] = df_active.apply(categorize_staff_enhanced, axis=1)

# Get unique job titles for sample
unique_titles = df_active[['HCM Job Title', 'HCM Job Family', 'Category']].drop_duplicates()
unique_titles = unique_titles.sort_values(['Category', 'HCM Job Title'])

print(f"\nTotal unique job titles: {len(unique_titles)}")
print("\nSAMPLE OF 50 JOB TITLES FOR VERIFICATION:")
print("-" * 80)
print(f"{'Job Title':<40} {'Job Family':<30} {'Category':<20}")
print("-" * 80)

sample = unique_titles.head(50)
for idx, row in sample.iterrows():
    title = str(row['HCM Job Title'])[:38] if pd.notna(row['HCM Job Title']) else 'N/A'
    family = str(row['HCM Job Family'])[:28] if pd.notna(row['HCM Job Family']) else 'N/A'
    category = row['Category']
    print(f"{title:<40} {family:<30} {category:<20}")

# Step 3: Count by category
category_counts = df_active['Category'].value_counts()
total_active = len(df_active)

field_eng = category_counts.get('Field Engineer', 0)
project_eng = category_counts.get('Project Engineer', 0)
superintendent = category_counts.get('Superintendent', 0)
non_ineight = category_counts.get('Non-InEight User', 0)

total_ineight = field_eng + project_eng + superintendent

print("\n" + "=" * 80)
print("STEP 3: CATEGORIZATION RESULTS (File 1)")
print("=" * 80)
print(f"\nTotal Active Staff: {total_active}")
print(f"  Field Engineers: {field_eng} ({field_eng/total_active*100:.1f}%)")
print(f"  Project Engineers: {project_eng} ({project_eng/total_active*100:.1f}%)")
print(f"  Superintendents: {superintendent} ({superintendent/total_active*100:.1f}%)")
print(f"  Non-InEight Users: {non_ineight} ({non_ineight/total_active*100:.1f}%)")
print(f"\n  TOTAL InEight Users: {total_ineight} ({total_ineight/total_active*100:.1f}%)")

# Step 4: Load second file for verification
print("\n" + "=" * 80)
print("STEP 4: VERIFICATION WITH SECOND FILE")
print("=" * 80)

try:
    df2 = pd.read_excel('cumberland_data_2.xlsx')
    print(f"Loaded {len(df2)} records from cumberland_data_2.xlsx")
    print(f"\nColumns: {df2.columns.tolist()}")
    
    # Apply same categorization
    if 'Assignment' in df2.columns:
        df2_active = df2[df2['Assignment'] == 'ACTIVE'].copy()
    else:
        df2_active = df2.copy()
    
    df2_active['Category'] = df2_active.apply(categorize_staff_enhanced, axis=1)
    
    category_counts2 = df2_active['Category'].value_counts()
    total_active2 = len(df2_active)
    
    field_eng2 = category_counts2.get('Field Engineer', 0)
    project_eng2 = category_counts2.get('Project Engineer', 0)
    superintendent2 = category_counts2.get('Superintendent', 0)
    non_ineight2 = category_counts2.get('Non-InEight User', 0)
    total_ineight2 = field_eng2 + project_eng2 + superintendent2
    
    print(f"\nTotal Active Staff (File 2): {total_active2}")
    print(f"  Field Engineers: {field_eng2} ({field_eng2/total_active2*100:.1f}%)")
    print(f"  Project Engineers: {project_eng2} ({project_eng2/total_active2*100:.1f}%)")
    print(f"  Superintendents: {superintendent2} ({superintendent2/total_active2*100:.1f}%)")
    print(f"  Non-InEight Users: {non_ineight2} ({non_ineight2/total_active2*100:.1f}%)")
    print(f"\n  TOTAL InEight Users: {total_ineight2} ({total_ineight2/total_active2*100:.1f}%)")
    
    # Average the percentages
    avg_field_pct = (field_eng/total_active + field_eng2/total_active2) / 2 * 100
    avg_project_pct = (project_eng/total_active + project_eng2/total_active2) / 2 * 100
    avg_super_pct = (superintendent/total_active + superintendent2/total_active2) / 2 * 100
    avg_ineight_pct = (total_ineight/total_active + total_ineight2/total_active2) / 2 * 100
    
    print("\n" + "-" * 80)
    print("AVERAGED PERCENTAGES (Both Files):")
    print(f"  Field Engineers: {avg_field_pct:.1f}%")
    print(f"  Project Engineers: {avg_project_pct:.1f}%")
    print(f"  Superintendents: {avg_super_pct:.1f}%")
    print(f"  TOTAL InEight Users: {avg_ineight_pct:.1f}%")
    
    # Use averaged percentages
    field_pct = avg_field_pct / 100
    project_pct = avg_project_pct / 100
    super_pct = avg_super_pct / 100
    ineight_pct = avg_ineight_pct / 100
    
except FileNotFoundError:
    print("cumberland_data_2.xlsx not found, using File 1 only")
    field_pct = field_eng / total_active
    project_pct = project_eng / total_active
    super_pct = superintendent / total_active
    ineight_pct = total_ineight / total_active

# Step 5: Apply to Kiewit with overhead adjustments
print("\n" + "=" * 80)
print("STEP 5: KIEWIT ENTERPRISE CALCULATION")
print("=" * 80)

kiewit_total_salary = 14946
district_overhead_pct = 10
corporate_overhead_pct = 10
total_overhead_pct = district_overhead_pct + corporate_overhead_pct
execution_staff_pct = 100 - total_overhead_pct

kiewit_district_overhead = int(kiewit_total_salary * district_overhead_pct / 100)
kiewit_corporate_overhead = int(kiewit_total_salary * corporate_overhead_pct / 100)
kiewit_execution_staff = int(kiewit_total_salary * execution_staff_pct / 100)

print(f"\nTotal Salaried Staff: {kiewit_total_salary:,}")
print(f"  District Overhead (10%): {kiewit_district_overhead:,}")
print(f"  Corporate/Home Office Overhead (10%): {kiewit_corporate_overhead:,}")
print(f"  Execution Staff (80%): {kiewit_execution_staff:,}")

# Apply InEight percentages to execution staff
kiewit_field_eng = int(kiewit_execution_staff * field_pct)
kiewit_project_eng = int(kiewit_execution_staff * project_pct)
kiewit_superintendent = int(kiewit_execution_staff * super_pct)
kiewit_total_ineight = kiewit_field_eng + kiewit_project_eng + kiewit_superintendent

print(f"\nInEight Users (Execution Staff Only):")
print(f"  Field Engineers: {kiewit_field_eng:,} ({field_pct*100:.1f}%)")
print(f"  Project Engineers: {kiewit_project_eng:,} ({project_pct*100:.1f}%)")
print(f"  Superintendents: {kiewit_superintendent:,} ({super_pct*100:.1f}%)")
print(f"  TOTAL: {kiewit_total_ineight:,} ({ineight_pct*100:.1f}%)")

# Step 6: Calculate hours and screen breakdown
print("\n" + "=" * 80)
print("STEP 6: HOURS & SCREEN BREAKDOWN")
print("=" * 80)

hours_per_year = 2080
ineight_usage_pct = 25
hours_in_ineight_per_person = hours_per_year * (ineight_usage_pct / 100)

print(f"\nAssumptions:")
print(f"  Hours per year per person: {hours_per_year}")
print(f"  InEight usage: {ineight_usage_pct}% of time")
print(f"  Hours in InEight per person per year: {hours_in_ineight_per_person}")

# Screen breakdown from screenshot
# Contract: 29, Control: 6, Core: 28, Design: 38, Inspect: 42, Billings: ~0, Plan: ~0
screen_counts = {
    'Contract': 29,
    'Control': 6,
    'Core': 28,
    'Design': 38,
    'Inspect': 42,
    'Billings': 0,
    'Plan': 0
}

total_screen_units = sum(screen_counts.values())
screen_percentages = {k: (v / total_screen_units * 100) if total_screen_units > 0 else 0 
                      for k, v in screen_counts.items()}

print(f"\nScreen Usage (from screenshot):")
print(f"  Total units: {total_screen_units}")
for screen, pct in screen_percentages.items():
    print(f"  {screen}: {screen_counts[screen]} units ({pct:.1f}%)")

# Calculate total hours by screen across all InEight users
total_ineight_hours = kiewit_total_ineight * hours_in_ineight_per_person

print(f"\nTotal InEight Hours (All Users):")
print(f"  {kiewit_total_ineight:,} users × {hours_in_ineight_per_person} hours = {total_ineight_hours:,.0f} hours/year")

print(f"\nHours by Screen (All InEight Users):")
for screen, pct in screen_percentages.items():
    hours = total_ineight_hours * (pct / 100)
    print(f"  {screen}: {hours:,.0f} hours ({pct:.1f}%)")

# Breakdown by role
print("\n" + "=" * 80)
print("HOURS BY ROLE AND SCREEN")
print("=" * 80)

for role, count in [('Field Engineers', kiewit_field_eng), 
                     ('Project Engineers', kiewit_project_eng),
                     ('Superintendents', kiewit_superintendent)]:
    role_hours_total = count * hours_in_ineight_per_person
    print(f"\n{role} ({count:,} people, {role_hours_total:,.0f} total hours):")
    for screen, pct in screen_percentages.items():
        hours = role_hours_total * (pct / 100)
        print(f"  {screen}: {hours:,.0f} hours ({pct:.1f}%)")

# Save comprehensive results
output_file = 'comprehensive_cumberland_analysis.txt'
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("COMPREHENSIVE CUMBERLAND PROJECT ANALYSIS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("KIEWIT ENTERPRISE ESTIMATION:\n")
    f.write(f"  Total Salaried Staff: {kiewit_total_salary:,}\n")
    f.write(f"  District Overhead (10%): {kiewit_district_overhead:,}\n")
    f.write(f"  Corporate Overhead (10%): {kiewit_corporate_overhead:,}\n")
    f.write(f"  Execution Staff (80%): {kiewit_execution_staff:,}\n\n")
    
    f.write("InEight Users:\n")
    f.write(f"  Field Engineers: {kiewit_field_eng:,} ({field_pct*100:.1f}%)\n")
    f.write(f"  Project Engineers: {kiewit_project_eng:,} ({project_pct*100:.1f}%)\n")
    f.write(f"  Superintendents: {kiewit_superintendent:,} ({super_pct*100:.1f}%)\n")
    f.write(f"  TOTAL: {kiewit_total_ineight:,} ({ineight_pct*100:.1f}%)\n\n")
    
    f.write(f"Total InEight Hours: {total_ineight_hours:,.0f} hours/year\n")
    f.write(f"  (Based on {hours_per_year} hours/year × {ineight_usage_pct}% usage)\n\n")
    
    f.write("Hours by Screen:\n")
    for screen, pct in screen_percentages.items():
        hours = total_ineight_hours * (pct / 100)
        f.write(f"  {screen}: {hours:,.0f} hours ({pct:.1f}%)\n")

print(f"\n\nResults saved to: {output_file}")

