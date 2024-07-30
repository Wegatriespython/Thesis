import numpy as np
from scipy import optimize

def worker_decision(savings, current_wage, expected_wage, current_price, historical_price, discount_factor=0.95, periods=40):
    def objective(x):
        consumption, wage, price = x
        return -calculate_utility(consumption, wage, savings, price, expected_wage, historical_price, discount_factor, periods)

    def constraint(x):
        consumption, wage, price = x
        return wage + savings - consumption * price  # Budget constraint

    # Set reasonable bounds
    min_consumption = 0.1
    max_consumption = max((savings + max(current_wage, expected_wage)) / max(current_price, 0.1), min_consumption)
    
    min_wage = max(0.9 * expected_wage, 0.1)
    max_wage = max(1.1 * expected_wage, min_wage * 1.05)

    min_price = max(0.9 * historical_price, 0.1)
    max_price = max(1.1 * historical_price, current_price * 1.05)  # Allow for higher price acceptance

    bounds = [(min_consumption, max_consumption), (min_wage, max_wage), (min_price, max_price)]

    initial_guess = [
        min(max_consumption, max(min_consumption, (savings + current_wage) / (2 * current_price))),
        expected_wage,
        max(historical_price, current_price)  # Start with the higher of historical or current price
    ]

    result = optimize.minimize(
        objective, 
        initial_guess,
        method='SLSQP', 
        bounds=bounds, 
        constraints={'type': 'ineq', 'fun': constraint}
    )

    if result.success:
        optimal_consumption, desired_wage, acceptable_price = result.x
    else:
        optimal_consumption, desired_wage, acceptable_price = initial_guess

    return optimal_consumption, acceptable_price, desired_wage

def calculate_utility(consumption, wage, savings, price, expected_wage, historical_price, discount_factor, periods):
    # Ensure all inputs are positive
    consumption = max(consumption, 0.01)
    wage = max(wage, 0.01)
    savings = max(savings, 0)
    price = max(price, 0.01)
    expected_wage = max(expected_wage, 0.01)
    historical_price = max(historical_price, 0.01)

    # Current period utility from consumption
    current_utility = np.log(consumption)

    # Incentive for higher wages
    wage_incentive = np.tanh((wage - expected_wage) / expected_wage)

    # Price expectation adjustment
    price_expectation = (price / historical_price - 1) * 0.5  # 50% weight to price changes
    price_adjusted_consumption = consumption * (1 - price_expectation)

    # Future utility from savings and expected consumption
    future_savings = savings + wage - (consumption * price)
    future_consumption = max(future_savings / (price * periods), 0.01)
    future_utility = sum(discount_factor**t * np.log(future_consumption) for t in range(1, periods + 1))

    # Combine all utility components
    total_utility = current_utility + wage_incentive + np.log(price_adjusted_consumption) + future_utility

    return total_utility