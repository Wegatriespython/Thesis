import random
from typing import List, Tuple, Any
from mesa_market_matching import market_matching

def generate_random_traders(num_traders: int, price_range: Tuple[float, float], quantity_range: Tuple[int, int]) -> List[Tuple[float, int, str]]:
    return [
        (round(random.uniform(*price_range), 2), random.randint(*quantity_range), f"Trader_{i}")
        for i in range(num_traders)
    ]

def verify_trades(original_buyers: List[Tuple[float, int, Any]], 
                  original_sellers: List[Tuple[float, int, Any]], 
                  transactions: List[Tuple[Any, Any, int, float]]) -> bool:
    # Check if all trades are valid (buyer price >= seller price)
    for buyer, seller, quantity, price in transactions:
        buyer_price = next(b[0] for b in original_buyers if b[2] == buyer)
        seller_price = next(s[0] for s in original_sellers if s[2] == seller)
        if buyer_price < seller_price or price > buyer_price or price < seller_price:
            print(f"Invalid trade: Buyer {buyer} price {buyer_price}, Seller {seller} price {seller_price}, Trade price {price}")
            return False

    # Check if no trader trades more than their initial quantity
    buyer_trades = {}
    seller_trades = {}
    for buyer, seller, quantity, _ in transactions:
        buyer_trades[buyer] = buyer_trades.get(buyer, 0) + quantity
        seller_trades[seller] = seller_trades.get(seller, 0) + quantity

    for _, quantity, buyer in original_buyers:
        if buyer_trades.get(buyer, 0) > quantity:
            print(f"Buyer {buyer} traded more than initial quantity")
            return False

    for _, quantity, seller in original_sellers:
        if seller_trades.get(seller, 0) > quantity:
            print(f"Seller {seller} traded more than initial quantity")
            return False

    # Check if the sum of traded quantities matches between buyers and sellers
    if sum(trade[2] for trade in transactions) != sum(buyer_trades.values()):
        print("Mismatch in total traded quantity")
        return False

    return True

def run_test_case(buyers, sellers, case_name: str):
    print(f"\nRunning test case: {case_name}")
    print("Buyers:", buyers)
    print("Sellers:", sellers)

    transactions = market_matching(buyers, sellers)

    print("\nTransactions:")
    for buyer, seller, quantity, price in transactions:
        print(f"{buyer} bought {quantity} from {seller} at price {price}")

    if verify_trades(buyers, sellers, transactions):
        print("Test case passed!")
    else:
        print("Test case failed!")

    return transactions

def run_tests():
    # Test case 1: Basic functionality
    buyers = [(10, 1, "B1"), (9, 2, "B2"), (5, 3, "B3")]
    sellers = [(8, 2, "S1"), (9, 3, "S2")]
    run_test_case(buyers, sellers, "Basic functionality")

    # Test case 2: No buyers
    buyers = []
    sellers = [(8, 2, "S1"), (9, 3, "S2")]
    run_test_case(buyers, sellers, "No buyers")

    # Test case 3: No sellers
    buyers = [(10, 1, "B1"), (9, 2, "B2"), (5, 3, "B3")]
    sellers = []
    run_test_case(buyers, sellers, "No sellers")

    # Test case 4: No matching trades (all seller prices too high)
    buyers = [(5, 1, "B1"), (4, 2, "B2"), (3, 3, "B3")]
    sellers = [(8, 2, "S1"), (9, 3, "S2")]
    run_test_case(buyers, sellers, "No matching trades (all seller prices too high)")

    # Test case 5: Exact matches in price and quantity
    buyers = [(10, 2, "B1"), (9, 3, "B2")]
    sellers = [(10, 2, "S1"), (9, 3, "S2")]
    run_test_case(buyers, sellers, "Exact matches in price and quantity")

    # Test case 6: Large disparities in quantity
    buyers = [(10, 100, "B1"), (9, 1, "B2")]
    sellers = [(8, 1, "S1"), (9, 200, "S2")]
    run_test_case(buyers, sellers, "Large disparities in quantity")

    # Test case 7: Random large dataset
    buyers = generate_random_traders(50, (1, 100), (1, 100))
    sellers = generate_random_traders(50, (1, 100), (1, 100))
    run_test_case(buyers, sellers, "Random large dataset")

if __name__ == "__main__":
    run_tests()