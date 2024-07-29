import unittest
from mesa_market_matching import market_matching

class TestMarketMatchingEdgeCases(unittest.TestCase):
    def test_oversupply_scenario(self):
        # Setup buyers and sellers similar to what we see in the log
        buyers = [
            (1, 1, "Worker1"),
            (1, 1, "Worker2"),
            (1, 1, "Worker3"),
            # ... add more workers as needed
        ]
        sellers = [
            (20.5, 1, "Firm1"),
            (20.5, 1, "Firm2"),
            (20.5, 1, "Firm3"),
            (20.5, 1, "Firm4"),
            (20.5, 1, "Firm5"),
        ]

        # Run the market matching function
        transactions = market_matching(buyers, sellers)

        # Assert that some transactions occur despite the price mismatch
        self.assertGreater(len(transactions), 0, "There should be some transactions even with oversupply")

        # Check that the number of transactions doesn't exceed the number of buyers
        self.assertLessEqual(len(transactions), len(buyers), "Number of transactions should not exceed number of buyers")

        # Verify that all transactions respect the budget constraints
        for buyer, seller, quantity, price in transactions:
            buyer_max_price = next(b[0] for b in buyers if b[2] == buyer)
            self.assertLessEqual(price, buyer_max_price, f"Transaction price {price} exceeds buyer's max price {buyer_max_price}")

if __name__ == '__main__':
    unittest.main()