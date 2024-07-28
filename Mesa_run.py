# Description: This file is used to run the model and visualize the results using the Mesa library.
from mesa_economy import EconomyModel
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.datacollection import DataCollector
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2

def collect_model_data(model):
    # Labor market
    labor_demand = sum(len(firm.workers) for firm in model.schedule.agents if hasattr(firm, 'workers'))
    labor_supply = sum(1 for agent in model.schedule.agents if isinstance(agent, Worker))

    # Capital goods market
    capital_demand = sum(firm.investment_demand for firm in model.schedule.agents if hasattr(firm, 'investment_demand'))
    capital_supply = sum(firm.inventory for firm in model.schedule.agents if isinstance(firm, Firm1))

    # Consumption goods market
    consumption_demand = sum(worker.calculate_desired_consumption() for worker in model.schedule.agents if isinstance(worker, Worker))
    consumption_supply = sum(firm.inventory for firm in model.schedule.agents if isinstance(firm, Firm2))

    return {
        "Labor Demand": labor_demand,
        "Labor Supply": labor_supply,
        "Capital Demand": capital_demand,
        "Capital Supply": capital_supply,
        "Consumption Demand": consumption_demand,
        "Consumption Supply": consumption_supply
    }

class EconomyModelWithPlots(EconomyModel):
    def __init__(self, num_workers, num_firm1, num_firm2):
        super().__init__(num_workers, num_firm1, num_firm2)
        self.datacollector = DataCollector(
            model_reporters={
                "Total Demand": lambda m: sum(firm.demand for firm in m.schedule.agents if hasattr(firm, 'demand')),
                "Total Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if hasattr(firm, 'inventory')),
                "Global Productivity": self.calculate_global_productivity,
                **{k: lambda m, k=k: collect_model_data(m)[k] for k in collect_model_data(self)}
            }
        )

# Create chart modules for each market
labor_chart = ChartModule([
    {"Label": "Labor Demand", "Color": "Blue"},
    {"Label": "Labor Supply", "Color": "Red"}
],
data_collector_name='datacollector')

capital_chart = ChartModule([
    {"Label": "Capital Demand", "Color": "Green"},
    {"Label": "Capital Supply", "Color": "Orange"}
],
data_collector_name='datacollector')

consumption_chart = ChartModule([
    {"Label": "Consumption Demand", "Color": "Purple"},
    {"Label": "Consumption Supply", "Color": "Brown"}
],
data_collector_name='datacollector')

# Create a chart for overall economic indicators
economy_chart = ChartModule([
    {"Label": "Total Demand", "Color": "Black"},
    {"Label": "Total Supply", "Color": "Red"},
    {"Label": "Global Productivity", "Color": "Green"}
],
data_collector_name='datacollector')

# Set up the server with all charts
server = ModularServer(EconomyModelWithPlots,
                       [labor_chart, capital_chart, consumption_chart, economy_chart],
                       "Economy Model",
                       {"num_workers": 20, "num_firm1": 2, "num_firm2": 5})

server.port = 8522  # The default

server.launch()