import unittest
import numpy as np
from Simple_profit_maxxing import simple_profit_maximization, cobb_douglas_production, guaranteed_global_profit_maximization
import matplotlib.pyplot as plt

class TestProfitMaximization(unittest.TestCase):

    def setUp(self):
        self.budget = 1000
        self.current_capital = 50
        self.current_labor = 10
        self.current_price = 10
        self.current_productivity = 1
        self.expected_demand = 100
        self.avg_wage = 5
        self.avg_capital_price = 20
        self.capital_elasticity = 0.3

    def run_test_with_method(self, method):
        optimal_labor, optimal_capital, optimal_price, optimal_production = method(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertGreater(optimal_labor, 0)
        self.assertGreater(optimal_capital, 0)
        self.assertGreater(optimal_price, 0)
        self.assertGreater(optimal_production, 0)

    def test_basic_optimization_simple(self):
        self.run_test_with_method(simple_profit_maximization)

    def test_basic_optimization_guaranteed(self):
        self.run_test_with_method(guaranteed_global_profit_maximization)

    def test_profit_improvement_simple(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = simple_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        initial_production = cobb_douglas_production(self.current_productivity, self.current_capital, self.current_labor, self.capital_elasticity)
        initial_revenue = self.current_price * min(initial_production, self.expected_demand)
        initial_cost = self.current_labor * self.avg_wage + self.current_capital * self.avg_capital_price
        initial_profit = initial_revenue - initial_cost

        optimal_revenue = optimal_price * optimal_production
        optimal_cost = optimal_labor * self.avg_wage + optimal_capital * self.avg_capital_price
        optimal_profit = optimal_revenue - optimal_cost

        self.assertGreater(optimal_profit, initial_profit)

    def test_profit_improvement_guaranteed(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = guaranteed_global_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        initial_production = cobb_douglas_production(self.current_productivity, self.current_capital, self.current_labor, self.capital_elasticity)
        initial_revenue = self.current_price * min(initial_production, self.expected_demand)
        initial_cost = self.current_labor * self.avg_wage + self.current_capital * self.avg_capital_price
        initial_profit = initial_revenue - initial_cost

        optimal_revenue = optimal_price * optimal_production
        optimal_cost = optimal_labor * self.avg_wage + optimal_capital * self.avg_capital_price
        optimal_profit = optimal_revenue - optimal_cost

        self.assertGreater(optimal_profit, initial_profit)

    def test_budget_constraint_simple(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = simple_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        total_cost = optimal_labor * self.avg_wage + max(0, optimal_capital - self.current_capital) * self.avg_capital_price
        self.assertLessEqual(total_cost, self.budget)

    def test_budget_constraint_guaranteed(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = guaranteed_global_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        total_cost = optimal_labor * self.avg_wage + max(0, optimal_capital - self.current_capital) * self.avg_capital_price
        self.assertLessEqual(total_cost, self.budget)

    def test_demand_constraint_simple(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = simple_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertLessEqual(optimal_production, self.expected_demand)

    def test_demand_constraint_guaranteed(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = guaranteed_global_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertLessEqual(optimal_production, self.expected_demand)

    def test_zero_budget_simple(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = simple_profit_maximization(
            0, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertEqual(optimal_labor, 0)
        self.assertEqual(optimal_capital, self.current_capital)
        self.assertGreater(optimal_price, 0)
        self.assertEqual(optimal_production, 0)

    def test_zero_budget_guaranteed(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production = guaranteed_global_profit_maximization(
            0, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertEqual(optimal_labor, 0)
        self.assertEqual(optimal_capital, self.current_capital)
        self.assertEqual(optimal_price, 0)
        self.assertEqual(optimal_production, 0)

    def test_high_wages_simple(self):
        high_wage = 1000
        optimal_labor, optimal_capital, optimal_price, optimal_production = simple_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, high_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertLess(optimal_labor, self.current_labor)

    def test_high_wages_guaranteed(self):
        high_wage = 1000
        optimal_labor, optimal_capital, optimal_price, optimal_production = guaranteed_global_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, high_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        self.assertLess(optimal_labor, self.current_labor)
    def test_convergence(self):
        # Call both methods with the same inputs
        simple_results = simple_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        guaranteed_results = guaranteed_global_profit_maximization(
            self.budget, self.current_capital, self.current_labor, self.current_price,
            self.current_productivity, self.expected_demand, self.avg_wage,
            self.avg_capital_price, self.capital_elasticity
        )

        # Compare the results
        self.assertAlmostEqual(simple_results[0], guaranteed_results[0], places=3)  # Labor
        self.assertAlmostEqual(simple_results[1], guaranteed_results[1], places=3)  # Capital
        self.assertAlmostEqual(simple_results[2], guaranteed_results[2], places=3)  # Price
        self.assertAlmostEqual(simple_results[3], guaranteed_results[3], places=3)  # Production


    def test_convergence_with_dataset(self):
        # Create a dataset of inputs
        budgets = np.linspace(0, 2000, 10)
        demands = np.linspace(50, 150, 10)
        wages = np.linspace(3, 7, 10)
        capital_prices = np.linspace(15, 25, 10)

        # Store results for plotting
        simple_results = []
        guaranteed_results = []

        for budget in budgets:
            for demand in demands:
                for wage in wages:
                    for capital_price in capital_prices:
                        simple_result = simple_profit_maximization(
                            budget, self.current_capital, self.current_labor, self.current_price,
                            self.current_productivity, demand, wage,
                            capital_price, self.capital_elasticity
                        )
                        guaranteed_result = guaranteed_global_profit_maximization(
                            budget, self.current_capital, self.current_labor, self.current_price,
                            self.current_productivity, demand, wage,
                            capital_price, self.capital_elasticity
                        )

                        simple_results.append(simple_result)
                        guaranteed_results.append(guaranteed_result)

        # Plot the results
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 2, 1)
        plt.scatter([result[0] for result in simple_results], [result[0] for result in guaranteed_results], label="Labor")
        plt.xlabel("Simple Labor")
        plt.ylabel("Guaranteed Labor")
        plt.legend()

        plt.subplot(2, 2, 2)
        plt.scatter([result[1] for result in simple_results], [result[1] for result in guaranteed_results], label="Capital")
        plt.xlabel("Simple Capital")
        plt.ylabel("Guaranteed Capital")
        plt.legend()

        plt.subplot(2, 2, 3)
        plt.scatter([result[2] for result in simple_results], [result[2] for result in guaranteed_results], label="Price")
        plt.xlabel("Simple Price")
        plt.ylabel("Guaranteed Price")
        plt.legend()

        plt.subplot(2, 2, 4)
        plt.scatter([result[3] for result in simple_results], [result[3] for result in guaranteed_results], label="Production")
        plt.xlabel("Simple Production")
        plt.ylabel("Guaranteed Production")
        plt.legend()

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    unittest.main()