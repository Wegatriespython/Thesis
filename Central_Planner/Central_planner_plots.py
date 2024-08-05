from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from Central_Planner.Central_planner import ImprovedMacroeconomicCentralPlanner

class CentralPlannerModel(Model):
    def __init__(self):
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.planner = ImprovedMacroeconomicCentralPlanner()
        self.current_step = 0
        self.datacollector = DataCollector(
            model_reporters={
                "Labor Supply": lambda m: m.planner.total_labor,
                "Labor Demand": lambda m: m.data['labor_firm1'] + m.data['labor_firm2'],
                "Capital Supply": lambda m: m.planner.total_capital,
                "Capital Demand": lambda m: m.data['capital_firm1'] + m.data['capital_firm2'],
                "Goods1 Supply": lambda m: m.calculate_goods_supply(1),
                "Goods1 Demand": lambda m: m.calculate_goods_demand(1),
                "Goods2 Supply": lambda m: m.calculate_goods_supply(2),
                "Goods2 Demand": lambda m: m.calculate_goods_demand(2),
                "Wage": lambda m: m.data['wage'],
                "Price Firm1": lambda m: m.data['price_firm1'],
                "Price Firm2": lambda m: m.data['price_firm2']
            }
        )
        self.data = self.planner.run_simulation(steps=1)[0]  # Initial data

    def step(self):
        self.current_step += 1
        self.data = self.planner.run_simulation(steps=1)[0]
        self.datacollector.collect(self)

    def calculate_goods_supply(self, firm):
        labor = self.data[f'labor_firm{firm}']
        capital = self.data[f'capital_firm{firm}']
        return self.planner.productivity * (capital ** 0.3) * (labor ** 0.7)  # Assuming capital elasticity of 0.3

    def calculate_goods_demand(self, firm):
        if firm == 1:
            return self.data['labor_firm2'] * self.data['wage'] / self.data['price_firm1']
        else:
            return self.planner.total_labor * self.data['wage'] / self.data['price_firm2']

def create_charts():
    charts = []
    for market in ['Labor', 'Capital', 'Goods1', 'Goods2']:
        charts.append(ChartModule([
            {"Label": f"{market} Supply", "Color": "Blue"},
            {"Label": f"{market} Demand", "Color": "Red"}
        ]))
    
    charts.append(ChartModule([
        {"Label": "Wage", "Color": "Green"},
        {"Label": "Price Firm1", "Color": "Orange"},
        {"Label": "Price Firm2", "Color": "Purple"}
    ]))
    
    return charts

server = ModularServer(CentralPlannerModel, create_charts(), "Central Planner Model")
server.port = 8521  # The default
server.launch()