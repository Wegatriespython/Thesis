from mesa_market_matching import market_matching
import numpy as np

def test_market_matching():
    print("Testing reverse double auction market matching function...")

    # Test case 1: Normal scenario (original)
    buyers = [(10, 100, 'B1'), (5, 95, 'B2'), (7, 98, 'B3')]
    sellers = [(8, 90, 'S1'), (6, 92, 'S2'), (10, 94, 'S3')]
    result = market_matching(buyers, sellers)
    print("Test case 1 result:", result)
    assert len(result) == 4, "Should have five trades"
    assert sum(trade[2] for trade in result) == 22, "Total quantity traded should be 22"
    assert all(trade[3] == 95 for trade in result), "All trades should be at price 94.5"

    # Test case 2: No matches possible (original)
    buyers = [(10, 80, 'B1'), (5, 85, 'B2')]
    sellers = [(8, 90, 'S1'), (6, 92, 'S2')]
    result = market_matching(buyers, sellers)
    print("Test case 2 result:", result)
    assert result == [], "Should have no trades"

    # Test case 3: Exact match (original)
    buyers = [(10, 100, 'B1')]
    sellers = [(10, 100, 'S1')]
    result = market_matching(buyers, sellers)
    print("Test case 3 result:", result)
    assert result == [('B1', 'S1', 10, 100.0)], "Should have one trade of 10 units at price 100"

    # Test case 4: Partial fulfillment (modified)
    buyers = [(15, 100, 'B1'), (10, 98, 'B2')]
    sellers = [(10, 95, 'S1'), (5, 97, 'S2')]
    result = market_matching(buyers, sellers)
    print("Test case 4 result:", result)
    assert len(result) == 2, "Should have two trades"
    assert sum(trade[2] for trade in result) == 15, "Total quantity traded should be 15"
    assert all(trade[3] == 97.5 for trade in result), "All trades should be at price 97.5"

    # Test case 5: Multiple buyers and sellers at clearing price (original)
    buyers = [(5, 100, 'B1'), (5, 100, 'B2'), (5, 100, 'B3')]
    sellers = [(5, 100, 'S1'), (5, 100, 'S2'), (5, 100, 'S3')]
    result = market_matching(buyers, sellers)
    print("Test case 5 result:", result)
    assert len(result) == 3, "Should have three trades"
    assert sum(trade[2] for trade in result) == 15, "Total quantity traded should be 15"
    assert all(trade[3] == 100 for trade in result), "All trades should be at price 100"

    # New Test case 6: Many sellers, few buyers
    buyers = [(50, 100, 'B1'), (30, 95, 'B2')]
    sellers = [(1, 90, f'S{i}') for i in range(1, 101)]  # 100 sellers with 1 unit each
    result = market_matching(buyers, sellers)
    print("Test case 6 result:", result)
    assert len(result) == 80, "Should have 80 trades"
    assert sum(trade[2] for trade in result) == 80, "Total quantity traded should be 80"
    assert all(trade[3] == 95 for trade in result), "All trades should be at price 95"

    # New Test case 7: Many buyers, few sellers
    buyers = [(1, 105, f'B{i}') for i in range(1, 101)]  # 100 buyers with 1 unit each
    sellers = [(40, 100, 'S1'), (40, 102, 'S2')]
    result = market_matching(buyers, sellers)
    print("Test case 7 result:", result)
    assert len(result) == 80, "Should have 80 trades"
    assert sum(trade[2] for trade in result) == 80, "Total quantity traded should be 80"
    assert all(trade[3] == 102.5 for trade in result), "All trades should be at price 102.5"

    print("All tests passed!")

if __name__ == "__main__":
    test_market_matching()
