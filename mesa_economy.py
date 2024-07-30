from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import logging
from Config import Config
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2
from mesa_market_matching import market_matching
from Accounting_System import GlobalAccountingSystem
import csv

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
        self.global_accounting = GlobalAccountingSystem()
        
        self.datacollector = DataCollector(
            model_reporters={
                "Total Labor": lambda m: m.global_accounting.total_labor,
                "Total Capital": lambda m: m.global_accounting.total_capital,
                "Total Goods": lambda m: m.global_accounting.total_goods,
                "Total Money": lambda m: m.global_accounting.total_money,
                "Average Market Demand": lambda m: m.global_accounting.get_average_market_demand(),
                "Average Capital Price": lambda m: m.global_accounting.get_average_capital_price(),
                "Average Wage": lambda m: m.global_accounting.get_average_wage(),
                "Average Inventory": self.calculate_average_inventory, 
                "Average Consumption Good Price": lambda m: m.global_accounting.get_average_consumption_good_price(),
                "Total Demand": lambda m: m.global_accounting.get_total_demand(),
                "Total Production": lambda m: m.global_accounting.get_total_production(),
                "Global Productivity": self.calculate_global_productivity,
            },
            agent_reporters={
                "Type": lambda a: type(a).__name__,
                "Capital": lambda a: a.accounts.assets.get('capital', 0) if hasattr(a, 'accounts') else None,
                "Cash": lambda a: a.accounts.assets.get('cash', 0) if hasattr(a, 'accounts') else None,
                "Inventory": lambda a: a.accounts.assets.get('inventory', 0) if hasattr(a, 'accounts') else None,
                "Labor": lambda a: len(a.workers) if hasattr(a, 'workers') else (1 if hasattr(a, 'employed') and a.employed else 0),
                "Revenue": lambda a: sum(a.accounts.income.values()) if hasattr(a, 'accounts') else None,
                "Expenses": lambda a: sum(a.accounts.expenses.values()) if hasattr(a, 'accounts') else None,
                "Profit": lambda a: a.accounts.calculate_profit() if hasattr(a, 'accounts') else None,
                "Productivity": lambda a: a.productivity if hasattr(a, 'productivity') else None,
                "Historic Price": lambda a: a.historic_price if isinstance(a, Worker) else None,
                "Wage": lambda a: a.wage if hasattr(a, 'wage') else None,
                "Skills": lambda a: a.skills if hasattr(a, 'skills') else None,
                "Savings": lambda a: a.savings if hasattr(a, 'savings') else None,
                "Consumption": lambda a: a.consumption if hasattr(a, 'consumption') else None
            }
        )


        self.create_agents()
        self.running = True
        for agent in self.schedule.agents:
            if isinstance(agent, (Firm1, Firm2)):
                self.global_accounting.register_firm(agent)

        print(f"Initializing EconomyModel with {num_workers} workers, {num_firm1} Firm1, and {num_firm2} Firm2")
        print(f"FIRM1_INITIAL_CAPITAL: {self.config.FIRM1_INITIAL_CAPITAL}")
        print(f"FIRM2_INITIAL_CAPITAL: {self.config.FIRM2_INITIAL_CAPITAL}")
    
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
            print(f"Initialized Firm1 {firm.unique_id} with capital: {firm.capital}")
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))

        for i in range(self.num_firm2):
            firm = Firm2(self.num_workers + self.num_firm1 + i, self)
            self.schedule.add(firm)
            print(f"Initialized Firm2 {firm.unique_id} with capital: {firm.capital}")
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(firm, (x, y))

    def step(self):
        self.step_count += 1
        logging.info(f"Starting step {self.step_count}")
        self.schedule.step()
        self.execute_labor_market()
        self.execute_capital_market()
        self.execute_consumption_market()
        self.update_agents_after_markets()
        self.global_accounting.check_consistency()
        self.datacollector.collect(self)
        self.global_accounting.reset_period_data()

        logging.info(f"Completed step {self.step_count}")


    def execute_labor_market(self):
        buyers = self.get_labor_buyers()
        sellers = self.get_labor_sellers()
        print("Labor Market")
        transactions = market_matching(buyers, sellers)
        self.process_labor_transactions(transactions)
        self.global_accounting.update_sellers([], sellers, [])

    def execute_capital_market(self):
        buyers = self.get_capital_buyers()
        sellers = self.get_capital_sellers()
        print("Capital Market")
        transactions = market_matching(buyers, sellers)
        self.process_capital_transactions(transactions)
        self.global_accounting.update_sellers(sellers, [], [])

    def execute_consumption_market(self):
        buyers = self.get_consumption_buyers()
        sellers = self.get_consumption_sellers()
        print("Consumption Market")
        transactions = market_matching(buyers, sellers)
        self.process_consumption_transactions(transactions)
        self.global_accounting.update_sellers([], [], sellers)
        self.update_price_history()
        
    def update_price_history(self):
        current_price = self.global_accounting.get_average_consumption_good_price()
        for agent in self.schedule.agents:
            if isinstance(agent, Worker):
                agent.price_history.append(current_price)
                if len(agent.price_history) > 10:  # Keep only last 10 periods
                    agent.price_history.pop(0)
                agent.historic_price = sum(agent.price_history) / len(agent.price_history)
    def get_labor_buyers(self):
        return [(firm.labor_demand, firm.get_max_wage(), firm) 
                for firm in self.schedule.agents 
                if isinstance(firm, (Firm1, Firm2)) and firm.labor_demand > 0]

    def get_labor_sellers(self):
        return [(1, worker.wage, worker) 
                for worker in self.schedule.agents 
                if isinstance(worker, Worker) and not worker.employed]

    def get_capital_buyers(self):
        return [(firm.investment_demand, firm.get_max_capital_price(), firm) 
                for firm in self.schedule.agents 
                if isinstance(firm, Firm2) and firm.investment_demand > 0]

    def get_capital_sellers(self):
        return [(firm.inventory, firm.price, firm) 
                for firm in self.schedule.agents 
                if isinstance(firm, Firm1) and firm.inventory > 0]

    def get_consumption_buyers(self):
        return [(worker.consumption, worker.get_max_consumption_price(), worker) 
                for worker in self.schedule.agents 
                if isinstance(worker, Worker) and worker.savings > 0]

    def get_consumption_sellers(self):
        return [(firm.inventory, firm.price, firm) 
                for firm in self.schedule.agents 
                if isinstance(firm, Firm2) and firm.inventory > 0]

    def process_labor_transactions(self, transactions):
        for firm, worker, quantity, price in transactions:
            firm.hire_worker(worker, price)
            worker.get_hired(firm, price)
            self.global_accounting.record_labor_transaction(firm, worker, quantity, price)
            self.global_accounting.update_average_wage()

    def process_capital_transactions(self, transactions):
        for buyer, seller, quantity, price in transactions:
            buyer.buy_capital(quantity, price)
            seller.sell_capital(quantity, price)
            self.global_accounting.record_capital_transaction(buyer, seller, quantity, price)
            self.global_accounting.update_average_capital_price()

    def process_consumption_transactions(self, transactions):
        for buyer, seller, quantity, price in transactions:
            buyer.consume(quantity, price)
            seller.sell_consumption_goods(quantity, price)
            self.global_accounting.record_consumption_transaction(buyer, seller, quantity, price)

    def update_agents_after_markets(self):
        for agent in self.schedule.agents:
            agent.update_after_markets()

    def get_total_demand(self):
        return sum(firm.accounts.get_total_demand() for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_total_supply(self):
        return sum(firm.accounts.assets.get('inventory', 0) for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))

    def get_capital_supply(self):
        return sum(firm.accounts.assets.get('inventory', 0) for firm in self.schedule.agents if isinstance(firm, Firm1))
    def calculate_average_inventory(self):
        firms = [agent for agent in self.schedule.agents if isinstance(agent, (Firm1, Firm2))]
        if firms:
            return sum(firm.inventory for firm in firms) / len(firms)
        return 0
    def calculate_global_productivity(self):
        total_output = sum(firm.accounts.get_total_production() for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))
        total_labor = self.global_accounting.get_total_labor()
        return total_output / total_labor if total_labor > 0 else 1

    
  