import timeit
import numpy as np
from Simple_profit_maxxing import (
    simple_profit_maximization,
    improved_gradient_descent_profit_maximization,
    neoclassical_profit_maximization
)

# Define test parameters
budget = 1000
current_capital = 50
current_labor = 10
current_price = 10
current_productivity = 1
expected_demand = 100
avg_wage = 5
avg_capital_price = 20
capital_elasticity = 0.3

# Define the number of runs for each function
number_of_runs = 1000

# Define the functions to be profiled
functions_to_profile = [
    simple_profit_maximization,
    improved_gradient_descent_profit_maximization,
    neoclassical_profit_maximization
]

# Profile each function
results = []
for func in functions_to_profile:
    # Use timeit to measure execution time
    execution_time = timeit.timeit(
        lambda: func(
            budget, current_capital, current_labor, current_price,
            current_productivity, expected_demand, avg_wage,
            avg_capital_price, capital_elasticity
        ),
        number=number_of_runs
    )
    
    # Calculate average execution time per run
    avg_execution_time = execution_time / number_of_runs
    
    results.append((func.__name__, avg_execution_time))

# Sort results by execution time (fastest first)
results.sort(key=lambda x: x[1])

# Print results
print(f"Performance profile over {number_of_runs} runs:")
print("-" * 50)
for name, time in results:
    print(f"{name:<40} {time:.6f} seconds")

# Calculate relative performance
fastest_time = results[0][1]
print("\nRelative Performance:")
print("-" * 50)
for name, time in results:
    relative_performance = time / fastest_time
    print(f"{name:<40} {relative_performance:.2f}x slower than fastest")

# Output:Performance profile over 1000 runs:
# --------------------------------------------------
# simple_profit_maximization               0.007312 seconds
# neoclassical_profit_maximization         0.009023 seconds
# improved_gradient_descent_profit_maximization 0.230018 seconds
#
# Relative Performance:
# --------------------------------------------------
# simple_profit_maximization               1.00x slower than fastest
# neoclassical_profit_maximization         1.23x slower than fastest
# improved_gradient_descent_profit_maximization 31.46x slower than fastest