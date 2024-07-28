import pandas as pd
import numpy as np

def analyze_optimization_log(file_path):
    df = pd.read_csv(file_path)
    
    print("Optimization Log Analysis:")
    
    # Calculate average discrepancies
    df['labor_discrepancy'] = df['optimal_labor'] - df['actual_labor']
    df['production_discrepancy'] = df['optimal_production'] - df['actual_production']
    df['price_discrepancy'] = df['optimal_price'] - df['actual_price']
    
    print("\nAverage Discrepancies:")
    print(f"Labor: {df['labor_discrepancy'].mean():.2f}")
    print(f"Production: {df['production_discrepancy'].mean():.2f}")
    print(f"Price: {df['price_discrepancy'].mean():.2f}")
    
    # Check for overproduction
    overproduction = (df['actual_production'] > df['optimal_production']).mean() * 100
    print(f"\nOverproduction Frequency: {overproduction:.2f}%")
    if overproduction > 20:
        print("WARNING: High frequency of overproduction!")
    
    # Analyze price setting behavior
    price_accuracy = (np.abs(df['actual_price'] - df['optimal_price']) / df['optimal_price']).mean() * 100
    print(f"Price Setting Accuracy: {100 - price_accuracy:.2f}%")
    if price_accuracy < 95:
        print("WARNING: Low price setting accuracy!")

def analyze_market_log(file_path):
    df = pd.read_csv(file_path)
    
    print("\nMarket Log Analysis:")
    
    markets = df['market'].unique()
    
    for market in markets:
        market_data = df[df['market'] == market]
        
        print(f"\n{market.capitalize()} Market:")
        
        # Calculate supply and demand
        supply = market_data[market_data['agent_type'] == 'seller']['quantity'].sum()
        demand = market_data[market_data['agent_type'] == 'buyer']['quantity'].sum()
        
        print(f"Total Supply: {supply}")
        print(f"Total Demand: {demand}")
        
        if market == 'labor' and supply > demand * 1.2:
            print(f"WARNING: Significant labor oversupply (Supply is {supply/demand:.2f}x Demand)")
        
        if market == 'capital' and demand == 0:
            print("WARNING: No recorded demand for capital!")
        
        # Analyze price volatility
        price_volatility = market_data.groupby('step')['price'].std().mean()
        print(f"Price Volatility (Avg. Standard Deviation): {price_volatility:.2f}")
        
        # Detect price spikes
        price_mean = market_data['price'].mean()
        price_std = market_data['price'].std()
        price_spikes = ((market_data['price'] > price_mean + 2*price_std) | (market_data['price'] < price_mean - 2*price_std)).mean() * 100
        print(f"Price Spike Frequency: {price_spikes:.2f}%")
        if price_spikes > 5:
            print(f"WARNING: High frequency of price spikes in the {market} market!")

# Run the analysis
analyze_optimization_log('optimization_log.csv')
analyze_market_log('market_log.csv')