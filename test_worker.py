import unittest
from utility_function import calculate_utility, worker_decision

class TestUtilityFunction(unittest.TestCase):

    def test_normal_inputs(self):
        utility = calculate_utility(50, 100, 1000, 1, 100, 1, 0.95, 40)
        self.assertGreater(utility, 0)

    def test_wage_deviation_penalty(self):
        base_utility = calculate_utility(50, 100, 1000, 1, 100, 1, 0.95, 40)
        higher_wage_utility = calculate_utility(50, 110, 1000, 1, 100, 1, 0.95, 40)
        lower_wage_utility = calculate_utility(50, 90, 1000, 1, 100, 1, 0.95, 40)
        self.assertGreater(base_utility, higher_wage_utility)
        self.assertGreater(base_utility, lower_wage_utility)

    def test_price_deviation_penalty(self):
        base_utility = calculate_utility(50, 100, 1000, 1, 100, 1, 0.95, 40)
        high_price_utility = calculate_utility(50, 100, 1000, 1.1, 100, 1, 0.95, 40)
        low_price_utility = calculate_utility(50, 100, 1000, 0.9, 100, 1, 0.95, 40)
        self.assertGreater(base_utility, high_price_utility)
        self.assertGreater(base_utility, low_price_utility)

class TestWorkerDecision(unittest.TestCase):

    def test_normal_inputs(self):
        consumption, price, wage = worker_decision(1000, 100, 100, 1, 1)
        self.assertGreater(consumption, 0)
        self.assertLess(consumption, 1100)  # Should not consume more than total resources
        self.assertGreater(price, 0.9)
        self.assertLess(price, 1.1)  # Price should be close to historical price
        self.assertGreater(wage, 90)
        self.assertLess(wage, 110)  # Wage should be close to expected wage

    def test_unemployed_scenario(self):
        consumption, price, wage = worker_decision(1000, 0, 100, 1, 1)
        self.assertGreater(consumption, 0)
        self.assertLess(consumption, 1000)  # Should not consume all savings
        self.assertGreater(price, 0.9)
        self.assertLess(price, 1.1)
        self.assertGreater(wage, 90)
        self.assertLess(wage, 100)  # Should be willing to work for less than expected when unemployed

    def test_high_historical_price(self):
        consumption, price, wage = worker_decision(1000, 100, 100, 1, 1.5)
        self.assertGreater(price, 1)  # Price should be higher due to high historical price
        self.assertLess(consumption, 1000)  # Consumption should be lower due to higher price

    def test_low_historical_price(self):
        consumption, price, wage = worker_decision(1000, 100, 100, 1, 0.75)
        self.assertLess(price, 1)  # Price should be lower due to low historical price
        self.assertGreater(consumption, 50)  # Consumption should be higher due to lower price

if __name__ == '__main__':
    unittest.main()