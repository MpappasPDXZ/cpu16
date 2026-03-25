#!/usr/bin/env python3
import pandas as pd

# Read the Excel file
df = pd.read_excel('employee_data_cumberland.xlsx')

print("=" * 80)
print("CUMBERLAND PROJECT STAFF ANALYSIS")
print("=" * 80)
print(f"\nTotal records: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
print("\n" + "=" * 80)
print("\nFirst 20 rows:")
print(df.head(20).to_string())
print("\n" + "=" * 80)

# Check for role/title columns
print("\n\nColumn analysis:")
for col in df.columns:
    print(f"\n{col}:")
    print(f"  Unique values: {df[col].nunique()}")
    if df[col].nunique() < 20:
        print(f"  Values: {df[col].unique().tolist()}")
    else:
        print(f"  Sample values: {df[col].unique()[:10].tolist()}")

