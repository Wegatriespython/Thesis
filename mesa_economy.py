from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import logging
import pandas as pd
import random
import numpy as np
from Config import Config
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2
from mesa_market_matching import market_matching
from Accounting_System import GlobalAccountingSystem
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

class EconomyModel(Model):
    def __init__(self, num_workers, num_firm1, num_firm2, mode):
        super().__init__()
        self.num_workers = num_workers
        self.num_firm1 = num_firm1
        self.num_firm2 = num_firm2
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.config = Config()
        self.step_count = 0
        self.global_accounting = GlobalAccountingSystem()  # Keep this for background data collection
        self.mode = mode
        self.data_collection = {}
        self.datacollector = DataCollector(
            model_reporters={
                "Total Labor": self.get_total_labor,
                "Total Capital": self.get_total_capital,
                "Total Goods": self.get_total_goods,
                "Total Money": self.get_total_money,
                "Average Market Demand": self.get_average_market_demand,
                "Average Capital Price": self.get_average_capital_price,
                "Average Wage": self.get_average_wage,
                "Average Inventory": self.calculate_average_inventory,
                "Average Consumption Good Price": self.get_average_consumption_good_price,
                "Total Demand": self.get_total_demand,
                "Total Production": self.get_total_production,
                "Global Productivity": self.calculate_global_productivity

            },
            agent_reporters={
                "Type": lambda a: type(a).__name__,
                "Capital": lambda a: getattr(a, 'capital', None),
                "Labor": lambda a: len(getattr(a, 'workers', [])),
                "Production": lambda a: getattr(a, 'production', None),
                "Price": lambda a: getattr(a, 'price', None),
                "Inventory": lambda a: getattr(a, 'inventory', None),
                "Budget": lambda a: getattr(a, 'budget', None),
                "Productivity": lambda a: getattr(a, 'productivity', None),
                "Wage": lambda a: getattr(a, 'wage', None),
                "Skills": lambda a: getattr(a, 'skills', None),
                "Savings": lambda a: getattr(a, 'savings', None),
                "Consumption": lambda a: getattr(a, 'consumption', None)
            }
        )

        self.create_agents()
        self.running = True
    def get_total_labor(self):
        return sum(len(firm.workers) for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_total_capital(self):
        return sum(firm.capital for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_total_goods(self):
        return sum(firm.inventory for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_total_money(self):
        return sum(firm.budget for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2))) + \
                sum(worker.savings for worker in self.schedule.agents if isinstance(worker, Worker))

    def get_average_market_demand(self):
        demands = [firm.expected_demand for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2))]
        return sum(demands) / len(demands) if demands else 0

    def get_average_capital_price(self):
        prices = [firm.price for firm in self.schedule.agents if isinstance(firm, Firm1)]
        return sum(prices) / len(prices) if prices else 0

    def get_average_wage(self):
        wages = [worker.wage for worker in self.schedule.agents if isinstance(worker, Worker) and worker.employed]
        return sum(wages) / len(wages) if wages else 0

    def get_average_consumption_good_price(self):
        prices = [firm.price for firm in self.schedule.agents if isinstance(firm, Firm2)]
        return sum(prices) / len(prices) if prices else 0

    def get_total_demand(self):
        return sum(firm.expected_demand for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_total_production(self):
        return sum(firm.production for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))
    def create_agents(self):
        # Create workers
        for i in range(self.num_workers):
            worker = Worker(i, self)
            self.schedule.add(worker)
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(worker, (x, y))

        # Create Firm1 instances
        for i in range(self.num_firm1):
            firm = Firm1(self.num_workers + i, self)
            self.schedule.add(firm)
            self.global_accounting.register_firm(firm)
            self.data_collection[firm.unique_id] = []  # Initialize data collection for this firm
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))

        # Create Firm2 instances
        for i in range(self.num_firm2):
            firm = Firm2(self.num_workers + self.num_firm1 + i, self)
            self.schedule.add(firm)
            self.global_accounting.register_firm(firm)
            self.data_collection[firm.unique_id] = []  # Initialize data collection for this firm
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))


    def step(self):
        if self.step_count == 100:
            print("Model Training Starts...")
            self.train_and_save_models()
            self.export_data_to_csv()  # Export data after training

        if self.mode == 'decentralised':
            self.run_decentralised_step()
        elif self.mode == 'centralised':
            self.run_centralised_step()
        else:
            raise ValueError("Invalid mode")
        # Analyze prediction accuracy every 10 steps
        #if self.step_count % 10 == 0:
         #   self.analyze_predictions()

        self.update_global_accounting()
        self.collect_data()
        self.datacollector.collect(self)
        self.global_accounting.reset_period_data()
        print(f"Step {self.step_count} completed")
        self.step_count += 1

    def collect_data(self):
        for firm in self.schedule.agents:
            if isinstance(firm, (Firm1, Firm2)):
                features = firm.prepare_features()
                actual_demand = firm.get_market_demand(firm.get_market_type())
                target = firm.sales
                if firm.unique_id not in self.data_collection:
                    self.data_collection[firm.unique_id] = []
                self.data_collection[firm.unique_id].append((features, actual_demand, target))
    def export_data_to_csv(self):
        all_data = []
        for firm_id, firm_data in self.data_collection.items():
            for features, actual_demand, sales in firm_data:
                row = list(features) + [actual_demand, sales, firm_id]
                all_data.append(row)

        columns = [
            'capital', 'num_workers', 'productivity', 'price', 'inventory', 'budget',
            'mean_historic_sales', 'std_historic_sales', 'avg_wage', 'avg_capital_price',
            'avg_consumption_good_price', 'market_demand', 'actual_demand', 'sales', 'firm_id'
        ]

        df = pd.DataFrame(all_data, columns=columns)
        df.to_csv('economic_model_data.csv', index=False)
        print("Data exported to economic_model_data.csv")
    def train_and_save_models(self):
        for firm_id, data in self.data_collection.items():
            X = np.array([d[0] for d in data])
            y_demand = np.array([d[1] for d in data])
            y_sales = np.array([d[2] for d in data])

            model_demand = LinearRegression()
            model_demand.fit(X, y_demand)

            model_sales = LinearRegression()
            model_sales.fit(X, y_sales)

            print(f"Firm {firm_id} - Trained demand model coefficients: {model_demand.coef_}")
            print(f"Firm {firm_id} - Trained sales model coefficients: {model_sales.coef_}")

            joblib.dump(model_demand, f'demand_predictor_firm_{firm_id}.joblib')
            joblib.dump(model_sales, f'sales_predictor_firm_{firm_id}.joblib')
    def analyze_predictions(self):
        for agent in self.schedule.agents:
            if isinstance(agent, (Firm1, Firm2)):
                agent.analyze_prediction_accuracy()
    def run_decentralised_step(self):
        self.update_worker_price_information()
        self.schedule.step()
        self.execute_markets()
    def run_centralised_step(self):
        planner_decisions = self.central_planner.optimize(self.get_current_state())
        self.apply_centralized_decisions(planner_decisions)

    def get_current_state(self):
        # New method to provide current state to central planner
        return {
            'workers': self.workers,
            'firms1': self.firm1s,
            'firms2': self.firm2s,
            'relative_price': self.relative_price,
            'total_labor': self.global_accounting.total_labor,
            'total_capital': self.global_accounting.total_capital,
            'total_goods': self.global_accounting.total_goods,
            'total_money': self.global_accounting.total_money,
        }

    def apply_centralized_decisions(self, decisions):
        # New method to apply central planner's decisions
        self.relative_price = decisions['relative_price']

        for firm, labor, capital, price in zip(self.firms, decisions['labor_allocation'],
                                                decisions['capital_allocation'], decisions['prices']):
            firm.apply_central_decision(labor, capital, price)

        for worker, employment, wage, consumption in zip(self.workers, decisions['employment'],
                                                            decisions['wages'], decisions['consumption']):
            worker.apply_central_decision(employment, wage, consumption)

        @property
        def workers(self):
            return [agent for agent in self.schedule.agents if isinstance(agent, Worker)]

        @property
        def firm1s(self):
            return [agent for agent in self.schedule.agents if isinstance(agent, Firm1)]

        @property
        def firm2s(self):
            return [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]

        @property
        def firms(self):
            return self.firm1s + self.firm

    def update_worker_price_information(self):
        consumption_firms = [firm for firm in self.schedule.agents if isinstance(firm, Firm2)]
        seller_prices = [firm.price for firm in consumption_firms]

        for agent in self.schedule.agents:
            if isinstance(agent, Worker):
                agent.set_seller_prices(seller_prices)
    def execute_markets(self):
        for agent in self.schedule.agents:
            if isinstance(agent, (Firm1, Firm2)):
                agent.update_firm_state()
        self.execute_labor_market()
        self.execute_capital_market()
        self.execute_consumption_market()

    def execute_labor_market(self):
        buyers = [(firm.labor_demand, firm.get_max_wage(), firm)
                  for firm in self.schedule.agents
                  if isinstance(firm, (Firm1, Firm2)) and firm.labor_demand > 0]
        sellers = [(1, worker.wage, worker)
                   for worker in self.schedule.agents
                   if isinstance(worker, Worker) and not worker.employed]

        transactions = market_matching(buyers, sellers)
        print("Labor Market Transaction", transactions)
        for firm, worker, quantity, price in transactions:
            firm.hire_worker(worker, price)
            worker.get_hired(firm, price)
            # Remove global_accounting.record_labor_transaction

    def execute_capital_market(self):
        buyers = [(firm.investment_demand, firm.get_max_capital_price(), firm)
                  for firm in self.schedule.agents
                  if isinstance(firm, Firm2) and firm.investment_demand > 0]
        sellers = [(firm.inventory, firm.price, firm)
                   for firm in self.schedule.agents
                   if isinstance(firm, Firm1) and firm.inventory > 0]

        transactions = market_matching(buyers, sellers)
        print("Capital Market Transaction", transactions)
        for buyer, seller, quantity, price in transactions:
            buyer.buy_capital(quantity, price)
            seller.sell_goods(quantity, price)
            # Remove global_accounting.record_capital_transaction

    def execute_consumption_market(self):
        buyers = [(worker.consumption, worker.get_max_consumption_price(), worker)
                  for worker in self.schedule.agents
                  if isinstance(worker, Worker) and worker.savings > 0]
        sellers = [(firm.inventory, firm.price, firm)
                   for firm in self.schedule.agents
                   if isinstance(firm, Firm2) and firm.inventory > 0]
        transactions = market_matching(buyers, sellers)
        print("Consumption Market Transaction", transactions)
        for buyer, seller, quantity, price in transactions:
            buyer.consume(quantity, price)
            seller.sell_goods(quantity, price)

    def update_global_accounting(self):
        total_demand = sum(firm.expected_demand for firm in self.global_accounting.firms)
        self.global_accounting.update_market_demand(total_demand)

    def calculate_average_inventory(self):
        firms = [agent for agent in self.schedule.agents if isinstance(agent, (Firm1, Firm2))]
        return sum(firm.inventory for firm in firms) / len(firms) if firms else 0

    def calculate_global_productivity(self):
        total_output = sum(firm.production for firm in self.global_accounting.firms)
        total_labor = self.global_accounting.total_labor
        return total_output / total_labor if total_labor > 0 else 0
