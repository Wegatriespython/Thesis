from typing import List, Tuple, NamedTuple, Any

class Trader(NamedTuple):
    price: float
    quantity: int
    id: str

class Trade(NamedTuple):
    buyer: str
    seller: str
    quantity: int
    price: float

def market_matching(buyers: List[Tuple[int, float, Any]], sellers: List[Tuple[int, float, Any]]) -> List[Tuple[Any, Any, int, float]]:
    """
    Match buyers and sellers based on their demand/supply and max/min prices.
    
    :param buyers: List of tuples (quantity, price, buyer_object)
    :param sellers: List of tuples (quantity, price, seller_object)
    :return: List of successful transactions (buyer_object, seller_object, quantity, price)
    """
    # Sort buyers (descending) and sellers (ascending) by price
    sorted_buyers = sorted(buyers, key=lambda x: x[1], reverse=True)
    sorted_sellers = sorted(sellers, key=lambda x: x[1])

    transactions = []
    buyer_index, seller_index = 0, 0

    while buyer_index < len(sorted_buyers) and seller_index < len(sorted_sellers):
        buyer_quantity, buyer_price, buyer_object = sorted_buyers[buyer_index]
        seller_quantity, seller_price, seller_object = sorted_sellers[seller_index]

        if seller_price > buyer_price:
            # No more viable trades possible
            break

        trade_quantity = min(buyer_quantity, seller_quantity)
        if trade_quantity > 0:
            transactions.append((buyer_object, seller_object, trade_quantity, seller_price))

            # Update quantities
            sorted_buyers[buyer_index] = (buyer_quantity - trade_quantity, buyer_price, buyer_object)
            sorted_sellers[seller_index] = (seller_quantity - trade_quantity, seller_price, seller_object)

        # Move pointers if quantity is exhausted
        if sorted_buyers[buyer_index][0] == 0:
            buyer_index += 1
        if sorted_sellers[seller_index][0] == 0:
            seller_index += 1
    print(f"Market Matching Input - Buyers: {buyers}, Sellers: {sellers}")
    print(f"Market Matching Output - Transactions: {transactions}")
    return transactions

# Test the function
if __name__ == "__main__":
    buyers = [(10, 1, "B1"), (9, 2, "B2"), (5, 3, "B3"), (4, 3, "B4"), (5, 3, "B5")]
    sellers = [(11, 2, "S1"), (9, 3, "S2"), (8, 1, "S3")]

    trades, unfulfilled_demand, unfulfilled_supply = market_matching(buyers, sellers)

    print("Executed Trades:")
    for trade in trades:
        print(f"{trade.buyer} bought {trade.quantity} from {trade.seller} at price {trade.price}")

    print("\nUnfulfilled Demand:")
    for buyer in unfulfilled_demand:
        print(f"{buyer.id}: {buyer.quantity} at {buyer.price}")

    print("\nUnfulfilled Supply:")
    for seller in unfulfilled_supply:
        print(f"{seller.id}: {seller.quantity} at {seller.price}")