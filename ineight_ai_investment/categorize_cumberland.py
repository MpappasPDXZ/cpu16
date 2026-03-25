#!/usr/bin/env python3
import pandas as pd

# Read the Excel file
df = pd.read_excel('employee_data_cumberland.xlsx')

# Filter to active assignments only
df_active = df[df['Assignment'] == 'ACTIVE'].copy()

print("=" * 80)
print("CUMBERLAND PROJECT - STAFF CATEGORIZATION")
print("=" * 80)
print(f"\nTotal Active Staff: {len(df_active)}")

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
category_percentages = (df_active['Category'].value_counts(normalize=True) * 100).round(1)

print("\n" + "=" * 80)
print("BREAKDOWN BY CATEGORY")
print("=" * 80)
print(f"\n{'Category':<25} {'Count':<10} {'Percentage':<10}")
print("-" * 45)
for category in ['Field Engineer', 'Project Engineer', 'Superintendent', 'Non-InEight User']:
    count = category_counts.get(category, 0)
    pct = category_percentages.get(category, 0)
    print(f"{category:<25} {count:<10} {pct:<10}%")

print(f"\n{'TOTAL':<25} {len(df_active):<10} {'100.0':<10}%")

# Show some examples from each category
print("\n" + "=" * 80)
print("SAMPLE EMPLOYEES BY CATEGORY")
print("=" * 80)

for category in ['Field Engineer', 'Project Engineer', 'Superintendent', 'Non-InEight User']:
    cat_df = df_active[df_active['Category'] == category]
    if len(cat_df) > 0:
        print(f"\n{category} ({len(cat_df)} total):")
        print(cat_df[['Employee', 'HCM Job Title', 'HCM Job Family']].head(10).to_string(index=False))
        if len(cat_df) > 10:
            print(f"... and {len(cat_df) - 10} more")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print(f"\nTotal Active Staff: {len(df_active)}")
print(f"\nInEight User Categories:")
print(f"  Field Engineers: {category_counts.get('Field Engineer', 0)} ({category_percentages.get('Field Engineer', 0):.1f}%)")
print(f"  Project Engineers: {category_counts.get('Project Engineer', 0)} ({category_percentages.get('Project Engineer', 0):.1f}%)")
print(f"  Superintendents: {category_counts.get('Superintendent', 0)} ({category_percentages.get('Superintendent', 0):.1f}%)")
print(f"\nNon-InEight Users: {category_counts.get('Non-InEight User', 0)} ({category_percentages.get('Non-InEight User', 0):.1f}%)")

# Save results
output_file = 'cumberland_staff_categorization.txt'
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("CUMBERLAND PROJECT - STAFF CATEGORIZATION\n")
    f.write("=" * 80 + "\n")
    f.write(f"\nTotal Active Staff: {len(df_active)}\n\n")
    f.write("BREAKDOWN BY CATEGORY\n")
    f.write("-" * 45 + "\n")
    for category in ['Field Engineer', 'Project Engineer', 'Superintendent', 'Non-InEight User']:
        count = category_counts.get(category, 0)
        pct = category_percentages.get(category, 0)
        f.write(f"{category:<25} {count:<10} {pct:<10}%\n")
    
    f.write(f"\n{'TOTAL':<25} {len(df_active):<10} {'100.0':<10}%\n")

print(f"\n\nResults saved to: {output_file}")

