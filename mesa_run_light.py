# Description: Run the EconomyModel with light analysis and CSV output using Mesa's DataCollector.
from mesa_economy import EconomyModel
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_model(steps, timeout=300):  # 5 minutes timeout
    model = EconomyModel(num_workers=20, num_firm1=2, num_firm2=5)
    for i in range(steps):
        model.step()
    return model

# Run the model
model = run_model(100)  # Run for 100 steps

if model:
    logging.info("Model completed successfully. Starting analysis...")
    
    # Get the dataframes from Mesa's DataCollector
    model_vars = model.datacollector.get_model_vars_dataframe()
    agent_vars = model.datacollector.get_agent_vars_dataframe()

    # Dump model-level data to CSV
    model_vars.to_csv('model_data.csv')
    logging.info("Model-level data has been dumped to model_data.csv")

    # Dump agent-level data to CSV
    agent_vars.to_csv('agent_data.csv')
    logging.info("Agent-level data has been dumped to agent_data.csv")

    # Perform analysis (you can keep your existing analysis here)
    print("\nModel-level Data Summary:")
    print(model_vars.describe())

    print("\nAgent-level Data Summary:")
    print(agent_vars.groupby('Type').last().describe())

else:
    logging.error("Model did not complete successfully. Unable to perform analysis.")