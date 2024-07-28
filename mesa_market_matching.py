def market_matching(buyers, sellers):
    """
    Match buyers and sellers based on their demand/supply and max/min prices.
    
    :param buyers: List of tuples (demand, max_price, buyer_object)
    :param sellers: List of tuples (supply, min_price, seller_object)
    :return: List of successful transactions (buyer, seller, quantity, price)
    """
    # Sort buyers by descending max price and sellers by ascending min price
    buyers.sort(key=lambda x: x[1], reverse=True)
    sellers.sort(key=lambda x: x[1])
    
    transactions = []
    
    i = 0
    while i < len(buyers):
        buyer_demand, max_price, buyer_obj = buyers[i]
        if buyer_demand <= 0:
            buyers.pop(i)
            continue
        
        j = 0
        while j < len(sellers):
            seller_supply, min_price, seller_obj = sellers[j]
            if seller_supply <= 0:
                sellers.pop(j)
                continue
            
            if min_price <= max_price:
                quantity = min(buyer_demand, seller_supply)
                price = (max_price + min_price) / 2  # Set price as average of max and min
                
                transactions.append((buyer_obj, seller_obj, quantity, price))
                
                buyer_demand -= quantity
                seller_supply -= quantity
                
                # Update the original lists
                buyers[i] = (buyer_demand, max_price, buyer_obj)
                sellers[j] = (seller_supply, min_price, seller_obj)
                
                if seller_supply == 0:
                    sellers.pop(j)
                else:
                    j += 1
                
                if buyer_demand == 0:
                    buyers.pop(i)
                    break
            else:
                j += 1  # Move to next seller if price is too high
        
        if buyer_demand > 0:
            i += 1  # Move to next buyer if demand not fully met
    
    return transactions