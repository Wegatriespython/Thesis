import numpy as np
from scipy.optimize import minimize

def simple_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
                               expected_demand, avg_wage, avg_capital_price, capital_elasticity):
    max_profit = float('-inf')
    optimal_labor = current_labor
    optimal_capital = current_capital
    optimal_price = current_price
    optimal_production = 0

    max_labor = budget / avg_wage
    max_capital = current_capital + budget / avg_capital_price

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

def neoclassical_profit_maximization(budget, current_capital, current_labor, current_price, current_productivity,
                                     expected_demand, avg_wage, avg_capital_price, capital_elasticity):
    def objective(x):
        labor, capital = x
        production = min(cobb_douglas_production(current_productivity, capital, labor, capital_elasticity), expected_demand)
        return -(current_price * production - (labor * avg_wage + (capital - current_capital) * avg_capital_price))

    def constraint(x):
        labor, capital = x
        return budget - (labor * avg_wage + (capital - current_capital) * avg_capital_price)

    max_labor = budget / avg_wage
    max_capital = current_capital + budget / avg_capital_price

    bounds = [(0, max_labor), (current_capital, max_capital)]
    constraints = {'type': 'ineq', 'fun': constraint}
    
    result = minimize(objective, [current_labor, current_capital], method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimal_labor, optimal_capital = result.x
        optimal_production = min(cobb_douglas_production(current_productivity, optimal_capital, optimal_labor, capital_elasticity), expected_demand)
        return optimal_labor, optimal_capital, current_price, optimal_production
    else:
        raise ValueError("Optimization failed: " + result.message)

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