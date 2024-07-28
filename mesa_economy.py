from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import logging
from Config import Config
from mesa_worker import Worker
import csv
from mesa_firm import Firm1, Firm2
from mesa_market_matching import market_matching

class EconomyModel(Model):
    def __init__(self, num_workers, num_firm1, num_firm2):
        super().__init__()
        self.num_workers = num_workers
        self.num_firm1 = num_firm1
        self.num_firm2 = num_firm2
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.config = Config()
        self.step_count = 0
        logging.info(f"EconomyModel initialized with {num_workers} workers, {num_firm1} Firm1, and {num_firm2} Firm2")
        self.average_market_demand = 0
        self.average_investment = 0
        self.average_consumption = 0
        self.average_capital_price = 0 
        self.labor_transactions = []
        self.capital_transactions = []
        self.consumption_transactions = []
        self.optimization_data = []
        self.market_data = []
        self.datacollector = DataCollector(
            model_reporters={
                "Total Demand": lambda m: sum(firm.demand for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
                "Total Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
                "Capital Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if isinstance(firm, Firm1)),
                "Global Productivity": self.calculate_global_productivity,
                "Average Market Demand": lambda m: m.average_market_demand,
                "Average Capital Price": lambda m: m.get_average_capital_price(),
                "Average Wage": lambda m: m.get_average_wage(),
                "Average Consumption Good Price": lambda m: m.get_average_consumption_good_price()
            },
            agent_reporters={
                "Type": lambda a: type(a).__name__,
                "Capital": lambda a: getattr(a, 'capital', None),
                "Productivity": lambda a: getattr(a, 'productivity', None),
                "Price": lambda a: getattr(a, 'price', None),
                "Inventory": lambda a: getattr(a, 'inventory', None),
                "Workers": lambda a: len(getattr(a, 'workers', [])),
                "Demand": lambda a: getattr(a, 'demand', None),
                "Production": lambda a: getattr(a, 'production', None),
                "Sales": lambda a: getattr(a, 'sales', None),
                "Employed": lambda a: getattr(a, 'employed', None),
                "Wage": lambda a: getattr(a, 'wage', None),
                "Skills": lambda a: getattr(a, 'skills', None),
                "Savings": lambda a: getattr(a, 'savings', None),
                "Consumption": lambda a: getattr(a, 'consumption', None)
            }
        )

        self.create_agents()
        self.running = True
        self.average_consumption = 0
        self.average_investment = 0

    def create_agents(self):
        for i in range(self.num_workers):
            worker = Worker(i, self)
            self.schedule.add(worker)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(worker, (x, y))

        for i in range(self.num_firm1):
            firm = Firm1(self.num_workers + i, self)
            self.schedule.add(firm)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))

        for i in range(self.num_firm2):
            firm = Firm2(self.num_workers + self.num_firm1 + i, self)
            self.schedule.add(firm)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))

    def step(self):
        self.step_count += 1
        self.labor_transactions = []
        self.capital_transactions = []
        self.consumption_transactions = []
        logging.info(f"Starting step {self.step_count}")
        self.datacollector.collect(self)
        self.schedule.step()
        self.update_economic_indicators()

        logging.info(f"Average market demand: {self.average_market_demand}")
        logging.info(f"Average capital price: {self.get_average_capital_price()}")
        logging.info(f"Average wage: {self.get_average_wage()}")

        self.execute_labor_market()
        self.execute_capital_market()
        self.execute_consumption_market()
        
        self.update_agents_after_markets()
        self.check_consistency()
        logging.info(f"Completed step {self.step_count}")
        self.log_data()  # Add this line at the end of the step method
  
    def update_economic_indicators(self):
        self.average_market_demand = self.calculate_average_market_demand()

    def calculate_average_market_demand(self):
        all_firms = [agent for agent in self.schedule.agents if isinstance(agent, (Firm1, Firm2))]
        total_demand = sum(firm.demand for firm in all_firms)
        return total_demand / len(all_firms) if all_firms else 0

    def get_average_capital_price(self):
        firm1s = [agent for agent in self.schedule.agents if isinstance(agent, Firm1)]
        if not firm1s:
            return self.config.INITIAL_PRICE
        return sum(firm.price for firm in firm1s) / len(firm1s)

    def get_average_wage(self):
        employed_workers = [agent for agent in self.schedule.agents 
                            if isinstance(agent, Worker) and agent.employed]
        if not employed_workers:
            return self.config.INITIAL_WAGE
        return sum(worker.wage for worker in employed_workers) / len(employed_workers)

    def get_average_consumption_good_price(self):
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]
        if not firm2s:
            return self.config.INITIAL_PRICE
        return sum(firm.price for firm in firm2s) / len(firm2s)

    def calculate_global_productivity(self):
        total_output = sum(firm.production for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))
        total_labor = sum(1 for worker in self.schedule.agents if isinstance(worker, Worker) and worker.employed)
        return total_output / total_labor if total_labor > 0 else 1


    def execute_labor_market(self):
        buyers = [(firm.labor_demand, firm.budget / firm.labor_demand if firm.labor_demand > 0 else 0, firm) 
                  for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)) and firm.labor_demand > 0]
        sellers = [(1, worker.wage, worker) for worker in self.schedule.agents if isinstance(worker, Worker) and not worker.employed]
        self.market_data.append(('labor', buyers, sellers))
        
        transactions = market_matching(buyers, sellers)

        self.labor_transactions = transactions
        
        for firm, worker, quantity, price in transactions:
            worker.employed = True
            worker.employer = firm
            worker.wage = price
            firm.workers.append(worker)
            firm.budget -= price
            firm.labor_demand -= quantity

    def execute_capital_market(self):
        buyers = [(firm.investment_demand, firm.budget / firm.investment_demand if firm.investment_demand > 0 else 0, firm) 
                  for firm in self.schedule.agents if isinstance(firm, Firm2) and firm.investment_demand > 0]
        sellers = [(firm.inventory, firm.price, firm) 
                   for firm in self.schedule.agents if isinstance(firm, Firm1) and firm.inventory > 0]
        self.market_data.append(('capital', buyers, sellers))
        
        transactions = market_matching(buyers, sellers)
        self.capital_transactions = transactions
        for buyer, seller, quantity, price in transactions:
            buyer.capital += quantity
            buyer.investment += quantity
            buyer.investment_demand -= quantity
            buyer.budget -= quantity * price
            
            seller.inventory -= quantity
            seller.sales += quantity
            seller.budget += quantity * price

    def execute_consumption_market(self):
        buyers = [(worker.calculate_desired_consumption(), worker.savings, worker) 
                  for worker in self.schedule.agents if isinstance(worker, Worker) and worker.savings > 0]
        sellers = [(firm.inventory, firm.price, firm) 
                   for firm in self.schedule.agents if isinstance(firm, Firm2) and firm.inventory > 0]
        self.market_data.append(('consumption', buyers, sellers))
        transactions = market_matching(buyers, sellers)
        self.consumption_transactions = transactions
        for buyer, seller, quantity, price in transactions:
            buyer.consumption += quantity
            buyer.savings -= quantity * price
            
            seller.inventory -= quantity
            seller.sales += quantity
            seller.budget += quantity * price

    def update_agents_after_markets(self):
        for agent in self.schedule.agents:
            if isinstance(agent, (Firm1, Firm2)):
                agent.demand = agent.sales  # Update demand based on actual sales
                agent.sales = 0  # Reset sales for next period
            elif isinstance(agent, Worker):
                agent.consumption = 0  # Reset consumption for next period
        
    def check_consistency(self):
        total_money = sum(agent.accounts.assets.get('cash', 0) for agent in self.schedule.agents)
        total_goods = sum(agent.inventory for agent in self.schedule.agents if isinstance(agent, (Firm1, Firm2)))
        total_labor = sum(1 for agent in self.schedule.agents if isinstance(agent, Worker) and agent.employed)

        expected_money = self.initial_money_supply
        expected_goods = self.initial_goods_supply
        expected_labor = self.num_workers

        assert abs(total_money - expected_money) < 1e-6, f"Money not conserved: {total_money} != {expected_money}"
        assert total_goods == expected_goods, f"Goods not conserved: {total_goods} != {expected_goods}"
        assert total_labor == expected_labor, f"Labor not conserved: {total_labor} != {expected_labor}"

    def log_data(self):
        # Log optimization data
        for firm in self.schedule.agents:
            if isinstance(firm, (Firm1, Firm2)):
                self.optimization_data.append({
                    'step': self.step_count,
                    'firm_id': firm.unique_id,
                    'firm_type': type(firm).__name__,
                    'optimal_labor': firm.labor_demand + len(firm.workers),
                    'optimal_capital': firm.capital,
                    'optimal_price': firm.price,
                    'optimal_production': firm.production,
                    'actual_labor': len(firm.workers),
                    'actual_capital': firm.capital,
                    'actual_price': firm.price,
                    'Inventory': firm.inventory
                })
    def write_logs(self):
        # Write optimization data
        with open('optimization_log.csv', 'w', newline='') as csvfile:
            fieldnames = ['step', 'firm_id', 'firm_type', 'optimal_labor', 'optimal_capital', 'optimal_price', 
                          'optimal_production', 'actual_labor', 'actual_capital', 'actual_price', 'Inventory']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.optimization_data:
                writer.writerow(row)

        # Write market data
        with open('market_log.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['step', 'market', 'agent_type', 'agent_id', 'quantity', 'price'])
            for step, (market, buyers, sellers) in enumerate(self.market_data):
                for quantity, price, agent in buyers:
                    writer.writerow([step + 1, market, 'buyer', agent.unique_id, quantity, price])
                for quantity, price, agent in sellers:
                    writer.writerow([step + 1, market, 'seller', agent.unique_id, quantity, price])