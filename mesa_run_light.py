# Description: Run the EconomyModel with light analysis and CSV output for transactions.
from mesa_economy import EconomyModel
import pandas as pd
import numpy as np
import signal
import logging
import csv
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_model(steps, timeout=300):  # 5 minutes timeout
    def handler(signum, frame):
        raise TimeoutError("Model execution timed out")

    signal.signal(signal.SIGABRT, handler)
    signal.alarm(timeout)

    transactions_data = defaultdict(list)

    try:
        model = EconomyModel(num_workers=20, num_firm1=2, num_firm2=5)
        for i in range(steps):
            logging.info(f"Starting step {i+1} of {steps}")
            model.step()
            
            # Collect transaction data
            transactions_data['labor'].extend([(i+1, *t) for t in model.labor_transactions])
            transactions_data['capital'].extend([(i+1, *t) for t in model.capital_transactions])
            transactions_data['consumption'].extend([(i+1, *t) for t in model.consumption_transactions])
            
            logging.info(f"Completed step {i+1} of {steps}")
        
        # Write transaction data to CSV
        with open('transactions.csv', 'w', newline='') as csvfile:
            fieldnames = ['step', 'market', 'buyer', 'seller', 'quantity', 'price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for market, transactions in transactions_data.items():
                for transaction in transactions:
                    writer.writerow({
                        'step': transaction[0],
                        'market': market,
                        'buyer': transaction[1].unique_id,
                        'seller': transaction[2].unique_id,
                        'quantity': transaction[3],
                        'price': transaction[4]
                    })
        
        logging.info("Transaction data written to transactions.csv")
        model.write_logs()
        return model.datacollector
    except TimeoutError as e:
        logging.error(f"Model execution timed out after {timeout} seconds")
        return None
    finally:
        signal.alarm(0)

# Run the model
collector = run_model(100)  # Run for 100 steps

if collector:
    # Analysis code here
    logging.info("Model completed successfully. Starting analysis...")
    
    # Get the dataframes
    model_vars = collector.get_model_vars_dataframe()
    agent_vars = collector.get_agent_vars_dataframe()

    # Analyze Firm1 (Capital Goods Producers)
    firm1_data = agent_vars.loc[(slice(None), [20, 21]), :]
    print("\nFirm1 (Capital Goods Producers) Analysis:")
    print(firm1_data.groupby(level=0).last())
    print("\nFirm1 Productivity Change:")
    print(firm1_data['Productivity'].groupby(level=1).agg(['first', 'last']))

    # Analyze Firm2 (Consumption Goods Producers)
    firm2_data = agent_vars.loc[(slice(None), range(22, 27)), :]
    print("\nFirm2 (Consumption Goods Producers) Analysis:")
    print(firm2_data.groupby(level=0).last())
    print("\nFirm2 Capital Growth:")
    print(firm2_data['Capital'].groupby(level=1).agg(['first', 'last']))

    # Analyze Workers
    worker_data = agent_vars.loc[(slice(None), range(20)), :]
    print("\nWorker Analysis:")
    print(worker_data.groupby(level=0).last().describe())

    # Analyze capital market
    print("\nCapital Market Analysis:")
    firm1_inventory = firm1_data['Inventory'].groupby(level=0).sum()
    firm2_demand = firm2_data['Demand'].groupby(level=0).sum()

    print(f"Final Capital Supply: {firm1_inventory.iloc[-1] if len(firm1_inventory) > 0 else 'N/A'}")
    print(f"Final Capital Demand: {firm2_demand.iloc[-1] if len(firm2_demand) > 0 else 'N/A'}")

    # Print final economic indicators
    print("\nFinal Economic Indicators:")
    print(f"Final Total Demand: {model_vars['Total Demand'].iloc[-1]:.2f}")
    print(f"Final Total Supply: {model_vars['Total Supply'].iloc[-1]:.2f}")
    print(f"Final Global Productivity: {model_vars['Global Productivity'].iloc[-1]:.2f}")
else:
    logging.error("Model did not complete successfully. Unable to perform analysis.")