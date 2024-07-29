import unittest
import numpy as np
from Simple_profit_maxxing import neoclassical_profit_maximization
import matplotlib.pyplot as plt

class TestProfitMaximization(unittest.TestCase):
    def setUp(self):
        self.budget = 1000
        self.current_capital = 50
        self.current_labor = 10
        self.current_price = 10
        self.current_productivity = 1
        self.avg_wage = 5
        self.avg_capital_price = 20
        self.capital_elasticity = 0.3
        self.depreciation_rate = 0.1

    def test_price_adjustment_with_inventory(self):
        expected_demands = np.linspace(10, 100, 10)
        inventory_levels = [0, 20, 50, 80]
        
        plt.figure(figsize=(12, 8))
        
        for inventory in inventory_levels:
            prices = []
            for demand in expected_demands:
                try:
                    _, _, price, _ = neoclassical_profit_maximization(
                        self.budget, self.current_capital, self.current_labor,
                        self.current_price, self.current_productivity, demand,
                        self.avg_wage, self.avg_capital_price, self.capital_elasticity,
                        inventory, self.depreciation_rate
                    )
                    prices.append(price)
                except ValueError as e:
                    print(f"Optimization failed for demand {demand} and inventory {inventory}: {str(e)}")
                    prices.append(np.nan)
            
            plt.plot(expected_demands, prices, label=f'Inventory: {inventory}')
        
        plt.xlabel('Expected Demand')
        plt.ylabel('Optimal Price')
        plt.title('Price Adjustment with Different Inventory Levels')
        plt.legend()
        plt.grid(True)
        plt.savefig('price_adjustment_test.png')
        plt.close()

        # Basic assertions
        self.assertTrue(any(not np.isnan(price) for price in prices), "At least one price should be calculated")

    def test_production_decision_with_inventory(self):
        expected_demands = np.linspace(10, 100, 10)
        inventory_levels = [0, 20, 50, 80]
        
        plt.figure(figsize=(12, 8))
        
        for inventory in inventory_levels:
            productions = []
            for demand in expected_demands:
                try:
                    _, _, _, production = neoclassical_profit_maximization(
                        self.budget, self.current_capital, self.current_labor,
                        self.current_price, self.current_productivity, demand,
                        self.avg_wage, self.avg_capital_price, self.capital_elasticity,
                        inventory, self.depreciation_rate
                    )
                    productions.append(production)
                except ValueError as e:
                    print(f"Optimization failed for demand {demand} and inventory {inventory}: {str(e)}")
                    productions.append(np.nan)
            
            plt.plot(expected_demands, productions, label=f'Inventory: {inventory}')
        
        plt.xlabel('Expected Demand')
        plt.ylabel('Optimal Production')
        plt.title('Production Decision with Different Inventory Levels')
        plt.legend()
        plt.grid(True)
        plt.savefig('production_decision_test.png')
        plt.close()

        # Basic assertions
        self.assertTrue(any(not np.isnan(prod) for prod in productions), "At least one production decision should be made")

    def test_price_stability(self):
        # Test that prices don't change too dramatically between small changes in demand
        demands = np.linspace(50, 55, 10)  # Small range of demands
        prices = []
        
        for demand in demands:
            try:
                _, _, price, _ = neoclassical_profit_maximization(
                    self.budget, self.current_capital, self.current_labor,
                    self.current_price, self.current_productivity, demand,
                    self.avg_wage, self.avg_capital_price, self.capital_elasticity,
                    0, self.depreciation_rate
                )
                prices.append(price)
            except ValueError as e:
                print(f"Optimization failed for demand {demand}: {str(e)}")
                prices.append(np.nan)
        
        valid_prices = [p for p in prices if not np.isnan(p)]
        if len(valid_prices) > 1:
            price_changes = np.diff(valid_prices)
            max_price_change = np.max(np.abs(price_changes))
            self.assertLess(max_price_change, 1, "Price should not change dramatically for small demand changes")
        else:
            print("Not enough valid prices to test stability")

if __name__ == '__main__':
    unittest.main()