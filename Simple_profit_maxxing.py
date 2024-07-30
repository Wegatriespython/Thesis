import numpy as np
from scipy.optimize import minimize
from Config import config

from typing import List
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

def neoclassical_profit_maximization(budget: float, current_capital: float, current_labor: float, 
                                     current_price: float, current_productivity: float,
                                     expected_demand: float, avg_wage: float, avg_capital_price: float, 
                                     capital_elasticity: float, current_inventory: float, 
                                     depreciation_rate: float, price_adjustment_factor: float,
                                     expected_periods: int, discount_rate: float, 
                                     historic_sales: List[float]):
    def objective(x):
        labor, capital, price = x
        total_discounted_profit = 0
        inventory = current_inventory
        
        for t in range(expected_periods):
            production = cobb_douglas_production(current_productivity, capital, labor, capital_elasticity)
            expected_sales = min(production + inventory, forecast_demand(price, t))
            revenue = price * expected_sales
            wage_cost = labor * avg_wage
            capital_cost = (capital - current_capital) * avg_capital_price if t == 0 else 0
            inventory_cost = depreciation_rate * price * max(inventory + production - expected_sales, 0)
            
            period_profit = revenue - wage_cost - capital_cost - inventory_cost
            total_discounted_profit += period_profit / ((1 + discount_rate) ** t)
            
            inventory = max(inventory + production - expected_sales, 0)

        return -total_discounted_profit  # Negative because we're minimizing

    def constraint(x):
        labor, capital, _ = x
        return budget - (labor * avg_wage + (capital - current_capital) * avg_capital_price)

    def forecast_demand(price: float, period: int) -> float:
        # Simple forecasting method using historical data and current price
        if not historic_sales:
            return expected_demand
        avg_historic_sales = np.mean(historic_sales)
        price_effect = (current_price / price) ** 1.5  # Assuming price elasticity of 1.5
        time_effect = 1 + (period * 0.02)  # Assuming 2% growth per period
        return avg_historic_sales * price_effect * time_effect

    max_labor = budget / avg_wage
    max_capital = current_capital + budget / avg_capital_price
    min_price = 0.5 * current_price
    max_price = 2 * current_price

    bounds = [(0, max_labor), (current_capital, max_capital), (min_price, max_price)]
    constraints = [{'type': 'ineq', 'fun': constraint}]

    initial_guess = [current_labor, current_capital, current_price]
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimal_labor, optimal_capital, optimal_price = result.x
        optimal_production = cobb_douglas_production(current_productivity, optimal_capital, optimal_labor, capital_elasticity)
    else:
        raise ValueError("Optimization failed: " + result.message)

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