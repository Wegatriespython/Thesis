import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from Simple_profit_maxxing import neoclassical_profit_maximization


class NeoclassicalFirm:
    def __init__(self, initial_capital, initial_price, initial_inventory, productivity_factor):
        self.capital = initial_capital
        self.price = initial_price
        self.inventory = initial_inventory
        self.labor = 10  # Initial labor
        self.production = 0
        self.sales = []
        self.prices = [initial_price]
        self.productions = [0]
        self.inventories = [initial_inventory]
        self.profits = []
        self.productivity_factor = productivity_factor
        self.market_share = 0.5
        self.historic_sales = []

    def make_decision(self, expected_demand, avg_wage, avg_capital_price, budget):
        optimal_labor, optimal_capital, optimal_price, optimal_production = neoclassical_profit_maximization(
            budget, self.capital, self.labor, self.price, self.productivity_factor,
            expected_demand, avg_wage, avg_capital_price, 0.3,  # capital_elasticity
            self.inventory, 0.1,  # depreciation_rate
            0.2,  # price_adjustment_factor
            5,  # expected_periods
            0.05,  # discount_rate
            self.historic_sales
        )
        self.labor = optimal_labor
        self.capital = optimal_capital
        self.price = optimal_price
        self.production = optimal_production







    def record_data(self):
        self.prices.append(self.price)
        self.productions.append(self.production)
        self.inventories.append(self.inventory)

def elastic_demand_curve(price, base_demand=1000, elasticity=-1.5):
    return base_demand * (price ** elasticity)

def run_neoclassical_competitive_simulation(num_periods=50):
    firm1 = NeoclassicalFirm(initial_capital=500, initial_price=20, initial_inventory=0, productivity_factor=1.05)
    firm2 = NeoclassicalFirm(initial_capital=450, initial_price=19, initial_inventory=1, productivity_factor=0.95)
    
    avg_wage = 20
    avg_capital_price = 100
    budget = 10000  # Initial budget for both firms

    for _ in range(num_periods):
        market_price = (firm1.price + firm2.price) / 2
        total_demand = elastic_demand_curve(market_price)
        
        # Firms make decisions
        firm1.make_decision(total_demand / 2, avg_wage, avg_capital_price, budget)
        firm2.make_decision(total_demand / 2, avg_wage, avg_capital_price, budget)

        # Calculate market shares based on prices
        total_price = firm1.price + firm2.price
        firm1.market_share = firm2.price / total_price
        firm2.market_share = firm1.price / total_price

        # Sales and inventory update
        firm1_sales = min(firm1.production + firm1.inventory, total_demand * firm1.market_share)
        firm2_sales = min(firm2.production + firm2.inventory, total_demand * firm2.market_share)
        firm1.update_inventory(firm1_sales)
        firm2.update_inventory(firm2_sales)

        # Record profits
        firm1_profit = firm1.price * firm1_sales - (firm1.labor * avg_wage + 0.05 * firm1.capital)
        firm2_profit = firm2.price * firm2_sales - (firm2.labor * avg_wage + 0.05 * firm2.capital)
        firm1.profits.append(firm1_profit)
        firm2.profits.append(firm2_profit)

        # Update budget for next period
        budget += (firm1_profit + firm2_profit) / 2

        # Record data
        firm1.record_data()
        firm2.record_data()

    return firm1, firm2

# Run simulation
firm1, firm2 = run_neoclassical_competitive_simulation()

# Plotting
plt.figure(figsize=(15, 10))

plt.subplot(2, 2, 1)
plt.plot(firm1.prices, label='Firm 1 Price')
plt.plot(firm2.prices, label='Firm 2 Price')
plt.title('Prices')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(firm1.productions, label='Firm 1 Production')
plt.plot(firm2.productions, label='Firm 2 Production')
plt.title('Production')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(firm1.inventories, label='Firm 1 Inventory')
plt.plot(firm2.inventories, label='Firm 2 Inventory')
plt.title('Inventory')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(firm1.profits, label='Firm 1 Profit')
plt.plot(firm2.profits, label='Firm 2 Profit')
plt.title('Profit')
plt.legend()

plt.tight_layout()
plt.show()

# Print final state
print(f"Final prices: Firm 1: {firm1.price:.2f}, Firm 2: {firm2.price:.2f}")
print(f"Final market shares: Firm 1: {firm1.market_share:.2%}, Firm 2: {firm2.market_share:.2%}")
print(f"Final profits: Firm 1: {firm1.profits[-1]:.2f}, Firm 2: {firm2.profits[-1]:.2f}")