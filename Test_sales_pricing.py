import unittest
import numpy as np
from Simple_profit_maxxing import neoclassical_profit_maximization
from utility_function import worker_decision

class TestCoreFunctions(unittest.TestCase):

    def test_profit_maximization_price_adjustment(self):
        # Test if prices fall when supply exceeds demand
        initial_price = 2.0
        initial_inventory = 100
        expected_demand = 50  # Low demand compared to inventory
        budget = 1000
        capital = 100
        labor = 10
        productivity = 1
        avg_wage = 5
        avg_capital_price = 20
        capital_elasticity = 0.3
        depreciation_rate = 0.1
        price_adjustment_factor = 0.2
        expected_periods = 5
        discount_rate = 0.05
        historic_sales = [60, 55, 50, 45, 40]  # Declining sales trend

        _, _, new_price, _ = neoclassical_profit_maximization(
            budget, capital, labor, initial_price, productivity, expected_demand,
            avg_wage, avg_capital_price, capital_elasticity, initial_inventory,
            depreciation_rate, price_adjustment_factor, expected_periods,
            discount_rate, historic_sales
        )

        self.assertLess(new_price, initial_price, 
                        "Price should decrease when supply (inventory) exceeds demand")

        # Test if prices rise when demand exceeds supply
        initial_price = 2.0
        initial_inventory = 50
        expected_demand = 100  # High demand compared to inventory
        historic_sales = [80, 85, 90, 95, 100]  # Increasing sales trend

        _, _, new_price, _ = neoclassical_profit_maximization(
            budget, capital, labor, initial_price, productivity, expected_demand,
            avg_wage, avg_capital_price, capital_elasticity, initial_inventory,
            depreciation_rate, price_adjustment_factor, expected_periods,
            discount_rate, historic_sales
        )

        self.assertGreater(new_price, initial_price, 
                           "Price should increase when demand exceeds supply (inventory)")

    def test_profit_maximization_negative_labor(self):
        # Test if the function produces negative labor demand
        initial_price = 10
        initial_inventory = 50
        expected_demand = 100
        budget = 1000
        capital = 100
        labor = 10
        productivity = 1
        avg_wage = 50  # High wage to potentially trigger negative labor demand
        avg_capital_price = 20
        capital_elasticity = 0.3
        depreciation_rate = 0.1
        price_adjustment_factor = 0.2
        expected_periods = 5
        discount_rate = 0.05
        historic_sales = [90, 95, 100, 105, 110]

        optimal_labor, _, _, _ = neoclassical_profit_maximization(
            budget, capital, labor, initial_price, productivity, expected_demand,
            avg_wage, avg_capital_price, capital_elasticity, initial_inventory,
            depreciation_rate, price_adjustment_factor, expected_periods,
            discount_rate, historic_sales
        )

        self.assertGreaterEqual(optimal_labor, 0, 
                                "Labor demand should not be negative")

    def test_worker_decision_wage_adjustment(self):
        # Test if worker's wage expectation adjusts to market conditions
        savings = 1000
        current_wage = 10
        expected_wage = 11
        current_price = 1
        historical_price = 1

        for _ in range(5):  # Simulate multiple periods
            consumption, price, wage = worker_decision(
                savings, current_wage, expected_wage, current_price, historical_price
            )
            
            savings -= consumption * price
            current_wage = 9  # Simulate wage decrease
            current_price *= 1.05  # Simulate inflation

        self.assertLess(wage, expected_wage, 
                        "Wage expectation should decrease after periods of lower wages and inflation")

    def test_worker_decision_consumption_adjustment(self):
        # Test if worker's consumption adjusts to changes in savings and prices
        initial_savings = 1000
        current_wage = 10
        expected_wage = 11
        current_price = 1
        historical_price = 1

        consumptions = []
        for _ in range(5):  # Simulate multiple periods
            consumption, price, _ = worker_decision(
                initial_savings, current_wage, expected_wage, current_price, historical_price
            )
            consumptions.append(consumption)
            
            initial_savings -= consumption * price
            current_price *= 1.1  # Simulate significant inflation

        self.assertTrue(any(consumptions[i] > consumptions[i+1] for i in range(len(consumptions)-1)), 
                        "Consumption should decrease at some point due to inflation and decreasing savings")

if __name__ == '__main__':
    unittest.main()