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
        model = EconomyModel(num_workers=20, num_firm1=2, num_firm2=5)
        for i in range(steps):
            model.step()
                 
    
        return model.datacollector

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

# Error message for future reference
"""
Traceback (most recent call last):
    File "C:\ProgramData\anaconda3\Lib\site-packages\pandas\core\indexes\base.py", line 3791, in get_loc
        return self._engine.get_loc(casted_key)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "index.pyx", line 152, in pandas._libs.index.IndexEngine.get_loc
    File "index.pyx", line 181, in pandas._libs.index.IndexEngine.get_loc
    File "pandas\_libs\hashtable_class_helper.pxi", line 7080, in pandas._libs.hashtable.PyObjectHashTable.get_item
    File "pandas\_libs\hashtable_class_helper.pxi", line 7088, in pandas._libs.hashtable.PyObjectHashTable.get_item
KeyError: 'Demand'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
    File "v:\Python Port\mesa_run_light.py", line 53, in <module>
        firm2_demand = firm2_data['Demand'].groupby(level=0).sum()
                                     ~~~~~~~~~~^^^^^^^^^^
    File "C:\ProgramData\anaconda3\Lib\site-packages\pandas\core\frame.py", line 3893, in __getitem__
        indexer = self.columns.get_loc(key)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\ProgramData\anaconda3\Lib\site-packages\pandas\core\indexes\base.py", line 3798, in get_loc
        raise KeyError(key) from err
KeyError: 'Demand'
"""
