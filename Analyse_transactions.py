import pandas as pd
import numpy as np

def analyze_transactions(file_path):
    df = pd.read_csv(file_path)
    df['step'] = pd.to_numeric(df['step'])

    markets = ['labor', 'capital', 'consumption']
    
    for market in markets:
        market_data = df[df['market'] == market]
        
        print(f"\n{market.capitalize()} Market Analysis:")
        
        # Calculate total quantity and average price
        total_quantity = market_data['quantity'].sum()
        avg_price = market_data['price'].mean()
        
        print(f"Total Transactions: {len(market_data)}")
        print(f"Total Quantity Traded: {total_quantity}")
        print(f"Average Price: {avg_price:.2f}")
        
        # Calculate price volatility
        price_volatility = market_data.groupby('step')['price'].std().mean()
        print(f"Price Volatility (Avg. Standard Deviation): {price_volatility:.2f}")
        
        # Analyze unique buyers and sellers
        unique_buyers = market_data['buyer'].nunique()
        unique_sellers = market_data['seller'].nunique()
        print(f"Unique Buyers: {unique_buyers}")
        print(f"Unique Sellers: {unique_sellers}")
        
        if market == 'labor':
            if unique_sellers > unique_buyers:
                print(f"Potential labor oversupply: {unique_sellers - unique_buyers} more sellers than buyers")
        
        if market == 'capital':
            if len(market_data) == 0:
                print("WARNING: No recorded transactions for capital!")
            elif unique_buyers == 0:
                print("WARNING: No buyers in the capital market!")
        
        if market == 'consumption':
            transactions_per_step = market_data.groupby('step').size()
            low_transaction_steps = (transactions_per_step < transactions_per_step.mean() / 2).sum()
            print(f"Steps with low transaction volume: {low_transaction_steps} out of {transactions_per_step.count()}")

# Run the analysis
analyze_transactions('transactions.csv')