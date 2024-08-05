import numpy as np
from scipy.optimize import minimize

# Model parameters
A = 1.0  # Productivity
rho = 0.5  # Elasticity parameter (0 < rho < 1)
beta = 0.95  # Discount factor
num_periods = 10
num_workers = 100
initial_capital = 1000
initial_assets_firm1 = 5000
initial_assets_firm2 = 5000
initial_worker_savings = 1000
min_wage = 1  # Minimum wage constraint

def ces_production(K, L):
    return A * (K**rho + L**rho)**(1/rho)

def objective(x):
    P1, P2, W, L1, K2 = x
    L2 = num_workers - L1
    
    # Production
    Q1 = ces_production(initial_capital, L1)
    Q2 = ces_production(K2, L2)
    
    # Profits and savings
    profit_firm1 = P1 * Q1 - W * L1
    profit_firm2 = P2 * Q2 - W * L2 - P1 * K2
    worker_consumption = W * num_workers / P2
    worker_savings = W * num_workers - P2 * worker_consumption
    
    # Present value calculations
    pv_profit_firm1 = sum([profit_firm1 * (beta ** t) for t in range(num_periods)])
    pv_profit_firm2 = sum([profit_firm2 * (beta ** t) for t in range(num_periods)])
    pv_worker_savings = sum([worker_savings * (beta ** t) for t in range(num_periods)])
    
    return -(pv_profit_firm1 + pv_profit_firm2 + pv_worker_savings)

def constraints(x):
    P1, P2, W, L1, K2 = x
    L2 = num_workers - L1
    
    Q1 = ces_production(initial_capital, L1)
    Q2 = ces_production(K2, L2)
    
    worker_consumption = W * num_workers / P2
    
    return np.array([
        initial_assets_firm1 - P1 * Q1 + W * L1,  # Firm 1 budget
        initial_assets_firm2 - P2 * Q2 + W * L2 + P1 * K2,  # Firm 2 budget
        initial_worker_savings - worker_consumption * P2 + W * num_workers,  # Worker budget
        worker_consumption - num_workers,  # Minimum consumption
        Q1 - K2,  # Capital goods market clearing
        Q2 - worker_consumption,  # Consumption goods market clearing
        L1 + L2 - num_workers,  # Labor market clearing
        W - min_wage,  # Minimum wage constraint
        L1, L2, K2  # Non-negativity constraints
    ])

# Initial guess
x0 = [20, 15, 10, 60, 400]  # P1, P2, W, L1, K2

# Bounds
bounds = [(1, None), (1, None), (min_wage, None), (0, num_workers), (0, initial_capital)]

# Solve the optimization problem
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints={'type': 'ineq', 'fun': constraints}, options={'ftol': 1e-8, 'maxiter': 1000})

# Extract results
P1, P2, W, L1, K2 = result.x
L2 = num_workers - L1

# Calculate quantities and other variables
Q1 = ces_production(initial_capital, L1)
Q2 = ces_production(K2, L2)
worker_consumption = W * num_workers / P2
profit_firm1 = P1 * Q1 - W * L1
profit_firm2 = P2 * Q2 - W * L2 - P1 * K2
worker_savings = W * num_workers - P2 * worker_consumption

# Print results
print("Optimization successful:", result.success)
print("Optimal prices and allocations:")
print(f"P1 (Capital goods price): {P1:.2f}")
print(f"P2 (Consumption goods price): {P2:.2f}")
print(f"W (Wage): {W:.2f}")
print(f"L1 (Labor in Firm 1): {L1:.2f}")
print(f"L2 (Labor in Firm 2): {L2:.2f}")
print(f"K2 (Capital bought by Firm 2): {K2:.2f}")
print(f"Q1 (Capital goods produced): {Q1:.2f}")
print(f"Q2 (Consumption goods produced): {Q2:.2f}")
print(f"Worker consumption: {worker_consumption:.2f}")
print(f"Profit Firm 1: {profit_firm1:.2f}")
print(f"Profit Firm 2: {profit_firm2:.2f}")
print(f"Worker savings: {worker_savings:.2f}")

# Verify constraints
constraint_values = constraints(result.x)
print("\nConstraint verification:")
print("All constraints should be non-negative:")
for i, value in enumerate(constraint_values):
    print(f"Constraint {i+1}: {value:.2e}")