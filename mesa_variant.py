from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from Config import Config
import random

class Worker(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.employed = False
        self.employer = None
        self.wage = self.model.config.INITIAL_WAGE
        self.savings = self.model.config.INITIAL_SAVINGS
        self.skills = self.model.config.INITIAL_SKILLS
        self.consumption = self.model.config.INITIAL_CONSUMPTION
        self.satiated = False

    def step(self):
        if self.consumption > 0:
            self.consumption = 0
        self.update_skills()

    def update_skills(self):
        if self.employed:
            self.skills *= (1 + self.model.config.SKILL_GROWTH_RATE)
        else:
            self.skills *= (1 - self.model.config.SKILL_DECAY_RATE)

    def calculate_desired_consumption(self):
        return min(self.wage * self.model.config.CONSUMPTION_PROPENSITY, self.savings)

class Firm1(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.capital = self.model.config.FIRM1_INITIAL_CAPITAL
        self.productivity = self.model.config.INITIAL_PRODUCTIVITY
        self.price = self.model.config.INITIAL_PRICE
        self.inventory = self.model.config.INITIAL_INVENTORY
        self.workers = []
        self.demand = self.model.config.INITIAL_DEMAND
        self.production = 0
        self.sales = 0
        self.budget = 0
        self.RD_investment = self.model.config.FIRM1_INITIAL_RD_INVESTMENT

    def step(self):
        self.innovate()
        self.produce()
        self.adjust_price()

    def innovate(self):
        if random.random() < self.model.config.INNOVATION_ATTEMPT_PROBABILITY:
            self.RD_investment = self.capital * self.model.config.FIRM1_RD_INVESTMENT_RATE
            if random.random() < self.model.config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity *= (1 + self.model.config.PRODUCTIVITY_INCREASE)

    def produce(self):
        if self.inventory < self.model.config.INVENTORY_THRESHOLD:
            self.production = self.cobb_douglas_production()
            self.production = max(0, min(self.production, self.demand - self.inventory))
            self.inventory += self.production
        else:
            self.production = 0

    def cobb_douglas_production(self):
        return self.model.config.TOTAL_FACTOR_PRODUCTIVITY * (self.capital ** self.model.config.CAPITAL_ELASTICITY) * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY))

    def adjust_price(self):
        marginal_cost = self.calculate_marginal_cost()
        self.price = max(1, (1 + self.model.config.MARKUP_RATE) * marginal_cost)

    def calculate_marginal_cost(self):
        if self.production > 0:
            return (sum(worker.wage for worker in self.workers) + self.capital * self.model.config.CAPITAL_RENTAL_RATE) / self.production
        return 0

class Firm2(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.capital = self.model.config.FIRM2_INITIAL_CAPITAL
        self.productivity = self.model.config.INITIAL_PRODUCTIVITY
        self.price = self.model.config.INITIAL_PRICE
        self.inventory = self.model.config.INITIAL_INVENTORY
        self.workers = []
        self.demand = self.model.config.INITIAL_DEMAND
        self.production = 0
        self.sales = 0
        self.budget = 0
        self.investment_demand = self.model.config.FIRM2_INITIAL_INVESTMENT_DEMAND
        self.investment = 0
        self.desired_capital = self.model.config.FIRM2_INITIAL_DESIRED_CAPITAL

    def step(self):
        self.calculate_investment_demand()
        self.produce()
        self.adjust_price()

    def calculate_investment_demand(self):
        if self.demand > 0 and len(self.workers) > 0:
            self.desired_capital = (self.demand / (self.model.config.TOTAL_FACTOR_PRODUCTIVITY * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY)))) ** (1 / self.model.config.CAPITAL_ELASTICITY)
            self.investment_demand = max(0, self.desired_capital - self.capital)
        else:
            self.investment_demand = 0

    def produce(self):
        if self.inventory < self.model.config.INVENTORY_THRESHOLD:
            self.production = self.cobb_douglas_production()
            self.production = max(0, min(self.production, self.demand - self.inventory))
            self.inventory += self.production
        else:
            self.production = 0

    def cobb_douglas_production(self):
        return self.model.config.TOTAL_FACTOR_PRODUCTIVITY * (self.capital ** self.model.config.CAPITAL_ELASTICITY) * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY))

    def adjust_price(self):
        marginal_cost = self.calculate_marginal_cost()
        self.price = max(1, (1 + self.model.config.MARKUP_RATE) * marginal_cost)

    def calculate_marginal_cost(self):
        if self.production > 0:
            return (sum(worker.wage for worker in self.workers) + self.capital * self.model.config.CAPITAL_RENTAL_RATE) / self.production
        return 0

class EconomyModel(Model):
    def __init__(self, num_workers, num_firm1, num_firm2):
        self.num_workers = num_workers
        self.num_firm1 = num_firm1
        self.num_firm2 = num_firm2
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.config = Config()  # You'll need to import or define the Config class
        self.datacollector = DataCollector(
            model_reporters={
                "Total Demand": lambda m: sum(firm.demand for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
                "Total Supply": lambda m: sum(firm.inventory for firm in m.schedule.agents if isinstance(firm, (Firm1, Firm2))),
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
                "Production": lambda a: getattr(a, 'production', None),
                "Sales": lambda a: getattr(a, 'sales', None),
                "Employed": lambda a: getattr(a, 'employed', None),
                "Wage": lambda a: getattr(a, 'wage', None),
                "Skills": lambda a: getattr(a, 'skills', None),
                "Savings": lambda a: getattr(a, 'savings', None),
                "Consumption": lambda a: getattr(a, 'consumption', None)
            }
        )

        # Create agents
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

        self.running = True

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

    def goods_market_clearing(self):
        firm1s = [agent for agent in self.schedule.agents if isinstance(agent, Firm1)]
        firm2s = [agent for agent in self.schedule.agents if isinstance(agent, Firm2)]

        all_firms = firm1s + firm2s
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

        self.average_investment = sum(firm.investment for firm in firm2s) / total_transactions if total_transactions > 0 else 0

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.labor_market_matching()
        self.capital_goods_market()
        self.consumption_market_matching()
        self.execute_consumption_sales()
        self.goods_market_clearing()

        # Update firms after market operations
        for firm in self.schedule.agents:
            if isinstance(firm, (Firm1, Firm2)):
                if isinstance(firm, Firm1):
                    firm.calculate_expected_demand(self.average_investment)
                else:
                    firm.calculate_expected_demand(self.average_consumption)