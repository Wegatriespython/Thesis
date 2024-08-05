def calculate_total_wage_income(wage, labor_supply):
    return wage * labor_supply

def consumption_function(income, price, consumption_propensity):
    return (income * consumption_propensity) / price

def update_worker_savings(current_savings, savings_change):
    print("The update is called", current_savings, savings_change)
    print("The new savings is", current_savings + savings_change)
    return current_savings + savings_change