def production_function(labor, capital, productivity, labor_share):
    return productivity * (labor ** labor_share) * (capital ** (1 - labor_share))

def calculate_profit(price, output, wage, labor, capital_rental_rate, capital):
    return price * output - wage * labor - capital_rental_rate * capital

def update_firm_assets(current_assets, profit):
    return current_assets + profit