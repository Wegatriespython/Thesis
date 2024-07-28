# Description: This file contains the EconomyModel class, which is the main class for the simulation. It contains the main logic for the simulation, including the labor market, goods market, and consumption market operations. The EconomyModel class is responsible for creating the agents, running the simulation, and collecting data for analysis. The EconomyModel class is a subclass of the Mesa Model class, which provides the basic functionality for running an agent-based model. The EconomyModel class uses the Mesa RandomActivation scheduler to run the simulation, and the Mesa MultiGrid to represent the spatial environment of the simulation. The EconomyModel class also uses the Mesa DataCollector to collect data on the model and the agents for analysis. The EconomyModel class contains methods for creating agents, running the simulation, and collecting data. The EconomyModel class also contains methods for labor market matching, goods market clearing, and consumption market matching. The EconomyModel class is the main class for the simulation and contains the main logic for the simulation.
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from Config import Config
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2

class EconomyModel(Model):
    def __init__(self, num_workers, num_firm1, num_firm2):
        super().__init__()  # Initialize the Mesa Model
        self.num_workers = num_workers
        self.num_firm1 = num_firm1
        self.num_firm2 = num_firm2
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.config = Config()
        self.datacollector = DataCollector(
        model_reporters={
            "Total Demand": lambda m: sum(firm.demand for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
            "Total Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
            "Capital Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if isinstance(firm, Firm1)),
            "Global Productivity": self.calculate_global_productivity
        },
            agent_reporters={
                "Type": lambda a: type(a).__name__,
                "Capital": lambda a: getattr(a, 'capital', None),
                "Productivity": lambda a: getattr(a, 'productivity', None),
                "Price": lambda a: getattr(a, 'price', None),
                "Inventory": lambda a: getattr(a, 'inventory', None),
                "Workers": lambda a: len(getattr(a, 'workers', [])),
                "Demand": lambda a: getattr(a, 'demand', None),
                "Inventory": lambda a: getattr(a, 'inventory', None),
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
        self.datacollector.collect(self)
        self.schedule.step()
        self.labor_market_matching()
        self.capital_goods_market()
        self.consumption_market_matching()
        self.execute_consumption_sales()
        self.goods_market_clearing()

    def calculate_global_productivity(self):
        total_output = sum(firm.production for firm in self.schedule.agents if isinstance(firm, (Firm1, Firm2)))
        total_labor = sum(1 for worker in self.schedule.agents if isinstance(worker, Worker) and worker.employed)
        return total_output / total_labor if total_labor > 0 else 1

    def labor_market_matching(self):
        all_firms = [agent for agent in self.schedule.agents if isinstance(agent, (Firm1, Firm2))]
        workers = [agent for agent in self.schedule.agents if isinstance(agent, Worker)]

        for firm in all_firms:
            firm.budget = firm.sales + firm.capital - sum(worker.wage for worker in firm.workers)
            workers_to_fire = []

            for worker in firm.workers:
                if firm.budget >= worker.wage:
                    firm.budget -= worker.wage
                    worker.savings += worker.wage
                else:
                    workers_to_fire.append(worker)
            
            for worker in workers_to_fire:
                firm.workers.remove(worker)
                worker.employed = False
                worker.employer = None
                worker.wage = 0

        available_workers = [w for w in workers if not w.employed]
        self.random.shuffle(available_workers)

        for worker in available_workers:
            hiring_firms = [f for f in all_firms if f.budget > self.config.MINIMUM_WAGE]
            if hiring_firms:
                hiring_firm = self.random.choice(hiring_firms)
                wage = min(hiring_firm.budget, self.config.INITIAL_WAGE)
                worker.employed = True
                worker.employer = hiring_firm
                worker.wage = wage
                hiring_firm.workers.append(worker)
                hiring_firm.budget -= wage

    def capital_goods_market(self):
        firm1s = [agent for agent in self.schedule.agents if isinstance(agent, Firm1)]
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]

        for firm1 in firm1s:
            firm1.demand = 0  # Reset demand for each Firm1

        for firm2 in firm2s:
            if firm2.investment_demand > 0:
                for firm1 in firm1s:
                    if firm1.inventory > 0:
                        quantity = min(firm2.investment_demand, firm1.inventory)
                        firm1.demand += quantity
                        firm2.investment_demand -= quantity
    def goods_market_clearing(self):
        firm1s = [agent for agent in self.schedule.agents if isinstance(agent, Firm1)]
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]

        total_transactions = 0

        for seller in firm1s:
            for buyer in firm2s:
                if seller.inventory > 0 and buyer.investment_demand > 0:
                    quantity = min(seller.inventory, buyer.investment_demand)
                    price = seller.price
                    if buyer.budget >= quantity * price:
                        seller.inventory -= quantity
                        seller.sales += quantity * price
                        buyer.capital += quantity
                        buyer.budget -= quantity * price
                        buyer.investment_demand -= quantity
                        total_transactions += 1

        self.average_investment = sum(firm.investment for firm in firm2s) / len(firm2s) if firm2s else 0

        # Update firms after market operations
        for firm in self.schedule.agents:
            if isinstance(firm, Firm1):
                firm.calculate_expected_demand(self.average_investment)
            elif isinstance(firm, Firm2):
                firm.calculate_expected_demand(self.average_consumption)
                
    def consumption_market_matching(self):
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]
        workers = [agent for agent in self.schedule.agents if isinstance(agent, Worker)]

        for firm in firm2s:
            firm.demand = 0  # Reset demand for each Firm2
            if firm.inventory > 0:
                for worker in workers:
                    desired_consumption = worker.calculate_desired_consumption()
                    if desired_consumption > 0:
                        quantity = min(firm.inventory, desired_consumption / firm.price)
                        firm.demand += quantity

    def execute_consumption_sales(self):
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]
        workers = [agent for agent in self.schedule.agents if isinstance(agent, Worker)]

        total_consumption = 0
        total_transactions = 0

        for firm in firm2s:
            for worker in workers:
                desired_consumption = worker.calculate_desired_consumption()
                if firm.inventory > 0 and desired_consumption > 0:
                    quantity = min(firm.inventory, desired_consumption / firm.price)
                    if worker.savings >= quantity * firm.price:
                        firm.inventory -= quantity
                        firm.sales += quantity * firm.price
                        worker.savings -= quantity * firm.price
                        worker.consumption += quantity
                        total_consumption += quantity
                        total_transactions += 1

        # Update worker satiation status
        for worker in workers:
            worker.satiated = (worker.consumption >= worker.calculate_desired_consumption())

        # Calculate average consumption for demand expectations
        self.average_consumption = total_consumption / total_transactions if total_transactions > 0 else 0

