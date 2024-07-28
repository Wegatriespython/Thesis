import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from Simple_profit_maxxing import simple_profit_maximization, cobb_douglas_production, improved_gradient_descent_profit_maximization, neoclassical_profit_maximization

# Define parameters (unchanged)
budget = 1000
current_capital = 50
current_labor = 10
current_price = 10
current_productivity = 1
expected_demand = 100
avg_wage = 5
avg_capital_price = 20
capital_elasticity = 0.3

# Define the full range of labor and capital values to explore
max_labor = budget / avg_wage
max_capital = current_capital + budget / avg_capital_price
labor_range = np.linspace(0, max_labor, 100)
capital_range = np.linspace(current_capital, max_capital, 100)

def calculate_ppf(labor):
    max_capital = current_capital + (budget - labor * avg_wage) / avg_capital_price
    production = cobb_douglas_production(current_productivity, max_capital, labor, capital_elasticity)
    return min(production, expected_demand)

ppf = np.array([calculate_ppf(l) for l in labor_range])

# Create meshgrid for 3D plotting
L, K = np.meshgrid(labor_range, capital_range)

# Calculate production possibilities for the PPF
production_ppf = np.minimum(
    cobb_douglas_production(current_productivity, K, L, capital_elasticity),
    expected_demand
)

# Calculate profit for each point
profit = current_price * production_ppf - (L * avg_wage + (K - current_capital) * avg_capital_price)

# Mask points that violate the budget constraint
budget_mask = (L * avg_wage + (K - current_capital) * avg_capital_price) <= budget
profit[~budget_mask] = np.nan

# Run optimizations
simple_labor, simple_capital, simple_price, simple_production = simple_profit_maximization(
    budget, current_capital, current_labor, current_price, current_productivity,
    expected_demand, avg_wage, avg_capital_price, capital_elasticity
)

grad_labor, grad_capital, grad_price, grad_production = improved_gradient_descent_profit_maximization(
    budget, current_capital, current_labor, current_price, current_productivity,
    expected_demand, avg_wage, avg_capital_price, capital_elasticity
)

neo_labor, neo_capital, neo_price, neo_production = neoclassical_profit_maximization(
    budget, current_capital, current_labor, current_price, current_productivity,
    expected_demand, avg_wage, avg_capital_price, capital_elasticity
)

# Calculate profits for each method
simple_profit = simple_price * simple_production - (simple_labor * avg_wage + (simple_capital - current_capital) * avg_capital_price)
grad_profit = grad_price * grad_production - (grad_labor * avg_wage + (grad_capital - current_capital) * avg_capital_price)
neo_profit = neo_price * neo_production - (neo_labor * avg_wage + (neo_capital - current_capital) * avg_capital_price)

# Create plots
fig = plt.figure(figsize=(18, 12))

# 3D surface plot
ax1 = fig.add_subplot(221, projection='3d')
surf = ax1.plot_surface(L, K, profit, cmap='viridis', alpha=0.8)
ax1.set_xlabel('Labor')
ax1.set_ylabel('Capital')
ax1.set_zlabel('Profit')
ax1.set_title('Profit Surface')
fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)

# Mark optimal points on 3D plot
ax1.scatter([simple_labor], [simple_capital], [simple_profit], color='red', s=100, label='Simple')
ax1.scatter([grad_labor], [grad_capital], [grad_profit], color='green', s=100, label='Gradient Descent')
ax1.scatter([neo_labor], [neo_capital], [neo_profit], color='blue', s=100, label='Neoclassical')
ax1.legend()

# Production Possibility Frontier
ax2 = fig.add_subplot(222)
ax2.plot(labor_range, ppf, label='PPF')
ax2.set_xlabel('Labor')
ax2.set_ylabel('Production')
ax2.set_title('Production Possibility Frontier')

# Mark optimal points on PPF plot
ax2.scatter(simple_labor, simple_production, color='red', s=100, label='Simple')
ax2.scatter(grad_labor, grad_production, color='green', s=100, label='Gradient Descent')
ax2.scatter(neo_labor, neo_production, color='blue', s=100, label='Neoclassical')

# Add budget constraint
ax2.plot([0, max_labor], [calculate_ppf(0), calculate_ppf(max_labor)], 'r--', label='Budget Constraint')

# Add demand constraint
ax2.axhline(y=expected_demand, color='g', linestyle='--', label='Demand Constraint')

ax2.legend()
ax2.grid(True)

# Comparison table
ax3 = fig.add_subplot(223)
ax3.axis('off')
table_data = [
    ['Method', 'Labor', 'Capital', 'Production', 'Profit'],
    ['Simple', f'{simple_labor:.2f}', f'{simple_capital:.2f}', f'{simple_production:.2f}', f'{simple_profit:.2f}'],
    ['Gradient Descent', f'{grad_labor:.2f}', f'{grad_capital:.2f}', f'{grad_production:.2f}', f'{grad_profit:.2f}'],
    ['Neoclassical', f'{neo_labor:.2f}', f'{neo_capital:.2f}', f'{neo_production:.2f}', f'{neo_profit:.2f}']
]
table = ax3.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)
ax3.set_title('Optimization Results Comparison')

plt.tight_layout()
plt.show()

# Print additional information
print(f"Budget: {budget}")
print(f"Expected demand: {expected_demand}")
print(f"Simple method - Budget used: {simple_labor * avg_wage + (simple_capital - current_capital) * avg_capital_price:.2f}")
print(f"Gradient Descent method - Budget used: {grad_labor * avg_wage + (grad_capital - current_capital) * avg_capital_price:.2f}")
print(f"Neoclassical method - Budget used: {neo_labor * avg_wage + (neo_capital - current_capital) * avg_capital_price:.2f}")