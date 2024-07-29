import unittest
from Simple_profit_maxxing import neoclassical_profit_maximization, simple_profit_maximization

class TestProfitMaximizationEdgeCases(unittest.TestCase):
    def test_zero_labor_scenario(self):
        # Setup parameters similar to what we see in the log
        budget = 25
        current_capital = 5
        current_labor = 0
        current_price = 1
        current_productivity = 1
        expected_demand = 2.5
        avg_wage = 0
        avg_capital_price = 0
        capital_elasticity = 0.3

        # Run the profit maximization function
        optimal_labor, optimal_capital, optimal_price, optimal_production =     simple_profit_maximization(
            budget, current_capital, current_labor, current_price,
            current_productivity, expected_demand, avg_wage,
            avg_capital_price, capital_elasticity
        )

        # Assert that the optimal production is not zero
        self.assertGreater(optimal_production, 0, "Optimal production should be greater than zero even with zero initial labor")
        
        # Assert that the optimal labor is not zero
        self.assertGreater(optimal_labor, 0, "Optimal labor should be greater than zero")

        # Check if the production meets the expected demand
        self.assertGreaterEqual(optimal_production, expected_demand, "Production should meet or exceed expected demand")

        # Ensure the budget constraint is respected
        total_cost = optimal_labor * avg_wage + (optimal_capital - current_capital) * avg_capital_price
        self.assertLessEqual(total_cost, budget, "Total cost should not exceed the budget")

if __name__ == '__main__':
    unittest.main()