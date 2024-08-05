import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("agent_data.csv")

# Group the data by agent type
grouped_df = df.groupby("Type")

# Calculate summary statistics for each agent type
summary_stats = grouped_df.agg(
    {
        "Labor": ["mean", "std"],
        "Revenue": ["mean", "std"],
        "Expenses": ["mean", "std"],
        "Profit": ["mean", "std"],
        "Productivity": ["mean", "std"],
        "Wage": ["mean", "std"],
        "Savings": ["mean", "std"],
        "Consumption": ["mean", "std"],
    }
)

# Print the summary statistics
print(summary_stats)

# Create a figure and axes for the plots
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 10))

# Plot the time series of labor for each agent type
for i, agent_type in enumerate(["Worker", "Firm1", "Firm2"]):
    grouped_df.get_group(agent_type).plot(x="Step", y="Labor", ax=axes[i, 0], title=f"{agent_type} Labor")

# Plot the time series of profit for each agent type
for i, agent_type in enumerate(["Worker", "Firm1", "Firm2"]):
    grouped_df.get_group(agent_type).plot(x="Step", y="Profit", ax=axes[i, 1], title=f"{agent_type} Profit")

# Plot the time series of savings for each agent type
for i, agent_type in enumerate(["Worker", "Firm1", "Firm2"]):
    grouped_df.get_group(agent_type).plot(x="Step", y="Savings", ax=axes[i, 2], title=f"{agent_type} Savings")

# Adjust layout and display the plots
plt.tight_layout()
plt.show()