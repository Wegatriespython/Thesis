import numpy as np

def market_matching(buyers, sellers):
    # Sort buyers (descending) and sellers (ascending) by price
    buyers.sort(key=lambda x: x[1], reverse=True)
    sellers.sort(key=lambda x: x[1])
    if not buyers or not sellers or buyers[0][1] < sellers[0][1]:
        return []  # No trades possible
    clearing_price = (buyers[0][1] + sellers[0][1]) / 2
    total_supply = sum(seller[0] for seller in sellers)
    transactions = []
    remaining_supply = total_supply
    buyer_index = 0
    while remaining_supply > 0 and buyer_index < len(buyers):
        for seller in sellers:
            if remaining_supply == 0 or buyer_index >= len(buyers):
                break

            buyer = buyers[buyer_index]
            trade_quantity = min(buyer[0], seller[0], remaining_supply)

            if trade_quantity > 0:
                transactions.append((buyer[2], seller[2], trade_quantity, clearing_price))
                remaining_supply -= trade_quantity
                seller = (seller[0] - trade_quantity, seller[1], seller[2])

                if buyer[0] > trade_quantity:
                    buyers[buyer_index] = (buyer[0] - trade_quantity, buyer[1], buyer[2])
                else:
                    buyer_index += 1

    return transactions
