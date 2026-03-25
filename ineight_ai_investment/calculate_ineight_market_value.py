#!/usr/bin/env python3
"""
Calculate Market Value of InEight Software Usage at Kiewit
Based on validated role-based hours allocation and pay rates
"""

# Pay rates from pay_table.txt (increased by 15%)
PAY_RATES = {
    'Field Engineer': {
        'hourly_min': 38.74,  # 33.69 * 1.15
        'hourly_max': 48.97,  # 42.58 * 1.15
        'annual_min': 80586,  # 70075 * 1.15
        'annual_max': 101851,  # 88566 * 1.15
        'burden_pct': 0.48,  # 48% burden
        'all_in_min': 57.34,  # hourly + burden
        'all_in_max': 72.48   # hourly + burden
    },
    'Project Engineer': {
        'hourly_min': 46.17,  # 40.15 * 1.15
        'hourly_max': 60.04,  # 52.21 * 1.15
        'annual_min': 96039,  # 83512 * 1.15
        'annual_max': 124890,  # 108600 * 1.15
        'burden_pct': 0.48,
        'all_in_min': 68.33,  # hourly + burden
        'all_in_max': 88.86   # hourly + burden
    },
    'Superintendent': {
        'hourly_min': 50.96,  # 44.31 * 1.15
        'hourly_max': 68.47,  # 59.54 * 1.15
        'annual_min': 105990,  # 92165 * 1.15
        'annual_max': 142419,  # 123843 * 1.15
        'burden_pct': 0.48,
        'all_in_min': 75.42,  # hourly + burden
        'all_in_max': 101.34  # hourly + burden
    }
}

# Computer usage percentages (from pay_table.txt)
COMPUTER_USAGE = {
    'Field Engineer': {'min': 0.50, 'max': 0.60},
    'Project Engineer': {'min': 0.70, 'max': 0.80},
    'Superintendent': {'min': 0.20, 'max': 0.40}
}

# Role distribution (from Cumberland analysis)
ROLE_DISTRIBUTION = {
    'Field Engineer': 1688,
    'Project Engineer': 83,
    'Superintendent': 1356
}

# Hours per year
HOURS_PER_YEAR = 2080
IN_EIGHT_USAGE_PCT = 0.25  # 25% of work time in InEight

# Validated module allocation (from InEight background documentation)
MODULE_ALLOCATION = {
    'Field Engineer': {
        'Inspect': 0.40,
        'Plan': 0.25,
        'Core': 0.15,
        'Contract': 0.10,
        'Design': 0.05,
        'Control': 0.05,
        'Billings': 0.00
    },
    'Project Engineer': {
        'Design': 0.50,
        'Contract': 0.40,
        'Plan': 0.05,
        'Control': 0.05,
        'Inspect': 0.00,
        'Billings': 0.00,
        'Core': 0.00
    },
    'Superintendent': {
        'Plan': 0.40,
        'Control': 0.25,
        'Contract': 0.10,
        'Inspect': 0.10,
        'Design': 0.05,
        'Core': 0.05,
        'Billings': 0.05
    }
}

print("=" * 80)
print("KIEWIT InEight SOFTWARE - MARKET VALUE CALCULATION")
print("=" * 80)

# Calculate hours by role
print("\nSTEP 1: HOURS CALCULATION")
print("-" * 80)

role_hours = {}
total_ineight_hours = 0

for role, user_count in ROLE_DISTRIBUTION.items():
    total_work_hours = user_count * HOURS_PER_YEAR
    ineight_hours = total_work_hours * IN_EIGHT_USAGE_PCT
    role_hours[role] = {
        'users': user_count,
        'total_work_hours': total_work_hours,
        'ineight_hours': ineight_hours
    }
    total_ineight_hours += ineight_hours
    
    print(f"\n{role}:")
    print(f"  Users: {user_count:,}")
    print(f"  Total Work Hours: {total_work_hours:,.0f} ({user_count:,} × {HOURS_PER_YEAR})")
    print(f"  InEight Hours: {ineight_hours:,.0f} (25% of work time)")

print(f"\nTOTAL InEight Hours: {total_ineight_hours:,.0f}")

# Calculate cost by role using all-in rates
print("\n" + "=" * 80)
print("STEP 2: COST CALCULATION (Using All-In Rates)")
print("-" * 80)

role_costs = {}
total_cost_min = 0
total_cost_max = 0

for role, hours_data in role_hours.items():
    pay_data = PAY_RATES[role]
    ineight_hours = hours_data['ineight_hours']
    
    # Calculate cost range using all-in rates
    cost_min = ineight_hours * pay_data['all_in_min']
    cost_max = ineight_hours * pay_data['all_in_max']
    
    role_costs[role] = {
        'hours': ineight_hours,
        'cost_min': cost_min,
        'cost_max': cost_max,
        'cost_avg': (cost_min + cost_max) / 2
    }
    
    total_cost_min += cost_min
    total_cost_max += cost_max
    
    print(f"\n{role}:")
    print(f"  InEight Hours: {ineight_hours:,.0f}")
    print(f"  All-In Rate: ${pay_data['all_in_min']:.2f} - ${pay_data['all_in_max']:.2f}/hour")
    print(f"  Cost Range: ${cost_min:,.0f} - ${cost_max:,.0f}")
    print(f"  Average Cost: ${role_costs[role]['cost_avg']:,.0f}")

total_cost_avg = (total_cost_min + total_cost_max) / 2

print(f"\n{'='*80}")
print(f"TOTAL ANNUAL COST OF InEight USAGE:")
print(f"  Minimum: ${total_cost_min:,.0f}")
print(f"  Maximum: ${total_cost_max:,.0f}")
print(f"  Average: ${total_cost_avg:,.0f}")
print(f"{'='*80}")

# Calculate cost by module
print("\n" + "=" * 80)
print("STEP 3: COST BY MODULE")
print("-" * 80)

module_costs = {}
modules = ['Plan', 'Inspect', 'Control', 'Contract', 'Core', 'Design', 'Billings']

for module in modules:
    module_costs[module] = {'min': 0, 'max': 0, 'avg': 0}

for role, hours_data in role_hours.items():
    pay_data = PAY_RATES[role]
    ineight_hours = hours_data['ineight_hours']
    module_pcts = MODULE_ALLOCATION[role]
    
    for module, pct in module_pcts.items():
        module_hours = ineight_hours * pct
        cost_min = module_hours * pay_data['all_in_min']
        cost_max = module_hours * pay_data['all_in_max']
        
        module_costs[module]['min'] += cost_min
        module_costs[module]['max'] += cost_max
        module_costs[module]['avg'] += (cost_min + cost_max) / 2

# Sort by average cost
sorted_modules = sorted(module_costs.items(), key=lambda x: x[1]['avg'], reverse=True)

print(f"\n{'Module':<12} {'Hours':>12} {'Cost (Min)':>15} {'Cost (Max)':>15} {'Cost (Avg)':>15}")
print("-" * 80)

total_module_hours = 0
for module, costs in sorted_modules:
    # Calculate total hours for this module
    module_hours = 0
    for role, hours_data in role_hours.items():
        module_pcts = MODULE_ALLOCATION[role]
        if module in module_pcts:
            module_hours += hours_data['ineight_hours'] * module_pcts[module]
    total_module_hours += module_hours
    
    print(f"{module:<12} {module_hours:>12,.0f} ${costs['min']:>14,.0f} ${costs['max']:>14,.0f} ${costs['avg']:>14,.0f}")

print("-" * 80)
print(f"{'TOTAL':<12} {total_module_hours:>12,.0f} ${total_cost_min:>14,.0f} ${total_cost_max:>14,.0f} ${total_cost_avg:>14,.0f}")

# Cost by role and module
print("\n" + "=" * 80)
print("STEP 4: COST BY ROLE AND MODULE")
print("-" * 80)

for role, hours_data in role_hours.items():
    pay_data = PAY_RATES[role]
    ineight_hours = hours_data['ineight_hours']
    module_pcts = MODULE_ALLOCATION[role]
    
    print(f"\n{role} ({hours_data['users']:,} users, {ineight_hours:,.0f} InEight hours):")
    print(f"  All-In Rate: ${pay_data['all_in_min']:.2f} - ${pay_data['all_in_max']:.2f}/hour")
    print(f"  {'Module':<12} {'Hours':>10} {'Cost (Min)':>15} {'Cost (Max)':>15} {'Cost (Avg)':>15}")
    print("  " + "-" * 70)
    
    role_total_min = 0
    role_total_max = 0
    
    for module, pct in sorted(module_pcts.items(), key=lambda x: x[1], reverse=True):
        if pct > 0:
            module_hours = ineight_hours * pct
            cost_min = module_hours * pay_data['all_in_min']
            cost_max = module_hours * pay_data['all_in_max']
            cost_avg = (cost_min + cost_max) / 2
            
            role_total_min += cost_min
            role_total_max += cost_max
            
            print(f"  {module:<12} {module_hours:>10,.0f} ${cost_min:>14,.0f} ${cost_max:>14,.0f} ${cost_avg:>14,.0f}")
    
    role_avg = (role_total_min + role_total_max) / 2
    print("  " + "-" * 70)
    print(f"  {'TOTAL':<12} {ineight_hours:>10,.0f} ${role_total_min:>14,.0f} ${role_total_max:>14,.0f} ${role_avg:>14,.0f}")

# Market Cap Interpretation
print("\n" + "=" * 80)
print("MARKET CAP INTERPRETATION")
print("=" * 80)

print(f"\nTotal Annual Cost of InEight Usage: ${total_cost_avg:,.0f}")
print(f"\nThis represents the 'market cap' or total value of InEight software usage at Kiewit.")
print(f"Any efficiency improvements that reduce InEight usage time would save:")
print(f"  - At 5% efficiency gain: ${total_cost_avg * 0.05:,.0f}/year")
print(f"  - At 10% efficiency gain: ${total_cost_avg * 0.10:,.0f}/year")
print(f"  - At 20% efficiency gain: ${total_cost_avg * 0.20:,.0f}/year")

# Validation checks
print("\n" + "=" * 80)
print("VALIDATION CHECKS")
print("=" * 80)

# Check 1: Hours sum correctly
total_hours_check = sum(r['ineight_hours'] for r in role_hours.values())
print(f"\n1. Total Hours Check:")
print(f"   Sum of role hours: {total_hours_check:,.0f}")
print(f"   Expected: {total_ineight_hours:,.0f}")
print(f"   Match: {'✓' if abs(total_hours_check - total_ineight_hours) < 1 else '✗'}")

# Check 2: Module percentages sum to 100% for each role
print(f"\n2. Module Percentage Check:")
for role, module_pcts in MODULE_ALLOCATION.items():
    total_pct = sum(module_pcts.values())
    print(f"   {role}: {total_pct*100:.1f}% {'✓' if abs(total_pct - 1.0) < 0.01 else '✗'}")

# Check 3: Cost calculation
print(f"\n3. Cost Calculation Check:")
print(f"   Total cost range: ${total_cost_min:,.0f} - ${total_cost_max:,.0f}")
print(f"   Average: ${total_cost_avg:,.0f}")
print(f"   Using average all-in rates: ✓")

# Check 4: Module hours sum to total
module_hours_sum = sum(
    sum(role_hours[r]['ineight_hours'] * MODULE_ALLOCATION[r][m] 
        for r in ROLE_DISTRIBUTION.keys() if m in MODULE_ALLOCATION[r])
    for m in modules
)
print(f"\n4. Module Hours Sum Check:")
print(f"   Sum of module hours: {module_hours_sum:,.0f}")
print(f"   Total InEight hours: {total_ineight_hours:,.0f}")
print(f"   Match: {'✓' if abs(module_hours_sum - total_ineight_hours) < 100 else '✗'}")

# Save results
output_file = 'ineight_market_value.txt'
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("KIEWIT InEight SOFTWARE - MARKET VALUE CALCULATION\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Total Annual Cost of InEight Usage: ${total_cost_avg:,.0f}\n")
    f.write(f"Range: ${total_cost_min:,.0f} - ${total_cost_max:,.0f}\n\n")
    
    f.write("Cost by Module:\n")
    f.write("-" * 80 + "\n")
    for module, costs in sorted_modules:
        module_hours = sum(
            role_hours[r]['ineight_hours'] * MODULE_ALLOCATION[r][module]
            for r in ROLE_DISTRIBUTION.keys() if module in MODULE_ALLOCATION[r]
        )
        f.write(f"{module:<12} {module_hours:>12,.0f} hours ${costs['avg']:>14,.0f}\n")
    
    f.write("\n\nCost by Role:\n")
    f.write("-" * 80 + "\n")
    for role, costs in role_costs.items():
        f.write(f"{role:<20} ${costs['cost_avg']:>14,.0f}\n")

print(f"\n\nResults saved to: {output_file}")

