# Description: Run the EconomyModel with visualizations using the current model structure and data collection methods
from mesa_economy import EconomyModel
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import Slider
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EconomyModelWithPlots(EconomyModel):
    def __init__(self, num_workers, num_firm1, num_firm2):
        super().__init__(num_workers, num_firm1, num_firm2)
        # The datacollector is already set up in the EconomyModel.__init__()

# Create chart modules based on the data collected in EconomyModel
labor_chart = ChartModule([
    {"Label": "Total Labor", "Color": "Blue"},
    {"Label": "Average Wage", "Color": "Red"}
], data_collector_name='datacollector')

capital_chart = ChartModule([
    {"Label": "Total Capital", "Color": "Green"},
    {"Label": "Average Capital Price", "Color": "Orange"}
], data_collector_name='datacollector')

goods_chart = ChartModule([
    {"Label": "Total Goods", "Color": "Purple"},
    {"Label": "Average Consumption Good Price", "Color": "Brown"}
], data_collector_name='datacollector')

economy_chart = ChartModule([
    {"Label": "Total Money", "Color": "Black"},
    {"Label": "Total Demand", "Color": "Red"},
    {"Label": "Total Production", "Color": "Green"},
    {"Label": "Global Productivity", "Color": "Blue"}
], data_collector_name='datacollector')

# Model parameters
model_params = {
    "num_workers": Slider("Number of Workers", 20, 1, 100, 1),
    "num_firm1": Slider("Number of Firm1", 2, 1, 10, 1),
    "num_firm2": Slider("Number of Firm2", 5, 1, 20, 1),
}

# Set up the server with all charts
server = ModularServer(EconomyModelWithPlots,
                       [labor_chart, capital_chart, goods_chart, economy_chart],
                       "Economy Model",
                       model_params)

if __name__ == "__main__":
    logging.info("Starting Economy Model server")
    server.port = 8522  # The default
    server.launch()