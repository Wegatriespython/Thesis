import numpy as np
from scipy.optimize import minimize
from Config import config
def simple_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
                               expected_demand, avg_wage, avg_capital_price, capital_elasticity):
    max_profit = float('-inf')
    optimal_labor = current_labor
    optimal_capital = current_capital
    optimal_price = current_price
    optimal_production = 0

    max_labor = budget / max(avg_wage, config.MINIMUM_WAGE)
    max_capital = current_capital + budget / max(avg_capital_price, config.INITIAL_PRICE)

    labor_range = np.linspace(0, max_labor, 100)
    capital_range = np.linspace(current_capital, max_capital, 100)

    for L in labor_range:
        for K in capital_range:
            if L * avg_wage + (K - current_capital) * avg_capital_price <= budget:
                Q = min(cobb_douglas_production(current_productivity, K, L, capital_elasticity), expected_demand)
                profit = current_price * Q - (L * avg_wage + (K - current_capital) * avg_capital_price)
                if profit > max_profit:
                    max_profit = profit
                    optimal_labor = L
                    optimal_capital = K
                    optimal_production = Q
    print(f"Profit Maximization Input - Budget: {budget}, Capital: {current_capital}, Labor: {current_labor}, Price: {current_price}, Productivity: {current_productivity}, Expected Demand: {expected_demand}, Avg Wage: {avg_wage}, Avg Capital Price: {avg_capital_price}")
    print(f"Profit Maximization Output - Optimal Labor: {optimal_labor}, Optimal Capital: {optimal_capital}, Optimal Price: {optimal_price}, Optimal Production: {optimal_production}")
    return optimal_labor, optimal_capital, current_price, optimal_production

def improved_gradient_descent_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
                                                  expected_demand, avg_wage, avg_capital_price, capital_elasticity,
                                                  learning_rate=0.01, max_iterations=10000, tolerance=1e-6):
    labor = current_labor
    capital = current_capital

    max_labor = budget / avg_wage
    max_capital = current_capital + budget / avg_capital_price

    for _ in range(max_iterations):
        production = min(cobb_douglas_production(current_productivity, capital, labor, capital_elasticity), expected_demand)
        profit = current_price * production - (labor * avg_wage + (capital - current_capital) * avg_capital_price)

        grad_labor = current_price * current_productivity * (1 - capital_elasticity) * (capital ** capital_elasticity) * (labor ** (-capital_elasticity)) - avg_wage
        grad_capital = current_price * current_productivity * capital_elasticity * (capital ** (capital_elasticity - 1)) * (labor ** (1 - capital_elasticity)) - avg_capital_price

        labor = np.clip(labor + learning_rate * grad_labor, 0, max_labor)
        capital = np.clip(capital + learning_rate * grad_capital, current_capital, max_capital)

        if np.abs(grad_labor) < tolerance and np.abs(grad_capital) < tolerance:
            break

    production = min(cobb_douglas_production(current_productivity, capital, labor, capital_elasticity), expected_demand)
    return labor, capital, current_price, production

from scipy.optimize import minimize

def neoclassical_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
                                     expected_demand, avg_wage, avg_capital_price, capital_elasticity, 
                                     current_inventory, depreciation_rate):
    def objective(x):
        labor, capital, price = x
        potential_production = cobb_douglas_production(current_productivity, capital, labor, capital_elasticity)
        
        # Consider current inventory
        total_available = current_inventory + potential_production
        sales = min(total_available, expected_demand)
        
        # Calculate revenue
        revenue = price * sales
        
        # Calculate costs
        production_cost = labor * avg_wage + (capital - current_capital) * avg_capital_price
        inventory_cost = current_inventory * depreciation_rate * price  # Opportunity cost of holding inventory
        
        return -(revenue - production_cost - inventory_cost)  # Negative because we're minimizing

    def constraint(x):
        labor, capital, _ = x
        return budget - (labor * avg_wage + (capital - current_capital) * avg_capital_price)

    max_labor = budget / avg_wage
    max_capital = current_capital + budget / avg_capital_price

    # Define bounds
    bounds = [(0, max_labor), (current_capital, max_capital), (0.1 * current_price, 10 * current_price)]

    # Define constraints
    constraints = [{'type': 'ineq', 'fun': constraint}]
    
    # If current inventory is sufficient, skip production
    if current_inventory >= expected_demand:
        optimal_labor = 0
        optimal_capital = current_capital
        optimal_price = current_price
        optimal_production = 0
    else:
        initial_guess = [current_labor, current_capital, current_price]
        result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

        if result.success:
            optimal_labor, optimal_capital, optimal_price = result.x
            optimal_production = max(0, cobb_douglas_production(current_productivity, optimal_capital, optimal_labor, capital_elasticity))
        else:
            raise ValueError("Optimization failed: " + result.message)

    print(f"Neoclassical Profit Maximization Results:")
    print(f"Optimal Labor: {optimal_labor}")
    print(f"Optimal Capital: {optimal_capital}")
    print(f"Optimal Price: {optimal_price}")
    print(f"Optimal Production: {optimal_production}")
    print(f"Expected Demand: {expected_demand}")
    print(f"Current Inventory: {current_inventory}")
    
    return optimal_labor, optimal_capital, optimal_price, optimal_production

def cobb_douglas_production(productivity, capital, labor, capital_elasticity):
    return productivity * (capital ** capital_elasticity) * (labor ** (1 - capital_elasticity))

# Example usage:
# budget = 1000
# current_capital = 50
# current_labor = 10
# current_price = 10
# current_productivity = 1
# expected_demand = 100
# avg_wage = 5
# avg_capital_price = 20
# capital_elasticity = 0.3

# simple_result = simple_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
#                                            expected_demand, avg_wage, avg_capital_price, capital_elasticity)
# grad_result = improved_gradient_descent_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
#                                                             expected_demand, avg_wage, avg_capital_price, capital_elasticity)
# neo_result = neoclassical_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
#                                               expected_demand, avg_wage, avg_capital_price, capital_elasticity)