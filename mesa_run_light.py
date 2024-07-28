# Description: Run the EconomyModel with light analysis.
from mesa_economy import EconomyModel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def run_model(steps):
    model = EconomyModel(num_workers=20, num_firm1=2, num_firm2=5)
    for i in range(steps):
        model.step()
    return model.datacollector

# Run the model
collector = run_model(100)  # Run for 100 steps

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

# Plot economic indicators
plt.figure(figsize=(12,6))
plt.plot(model_vars['Total Demand'], label='Total Demand')
plt.plot(model_vars['Total Supply'], label='Total Supply')
plt.plot(model_vars['Global Productivity'], label='Global Productivity')
plt.legend()
plt.title('Economic Indicators')
plt.xlabel('Step')
plt.ylabel('Value')
plt.show()

# Analyze capital market
print("\nCapital Market Analysis:")
firm1_inventory = firm1_data['Inventory'].groupby(level=0).sum() if 'Inventory' in firm1_data.columns else np.zeros(100)
firm2_demand = firm2_data['Demand'].groupby(level=0).sum() if 'Demand' in firm2_data.columns else np.zeros(100)

plt.figure(figsize=(12,6))
plt.plot(firm1_inventory, label='Capital Supply (Firm1 Inventory)')
plt.plot(firm2_demand, label='Capital Demand (Firm2 Demand)')
plt.legend()
plt.title('Capital Market Dynamics')
plt.xlabel('Step')
plt.ylabel('Value')
plt.show()

print(f"Final Capital Supply: {firm1_inventory.iloc[-1] if len(firm1_inventory) > 0 else 'N/A'}")
print(f"Final Capital Demand: {firm2_demand.iloc[-1] if len(firm2_demand) > 0 else 'N/A'}")

# Print final economic indicators
print("\nFinal Economic Indicators:")
print(f"Final Total Demand: {model_vars['Total Demand'].iloc[-1]:.2f}")
print(f"Final Total Supply: {model_vars['Total Supply'].iloc[-1]:.2f}")
print(f"Final Global Productivity: {model_vars['Global Productivity'].iloc[-1]:.2f}")