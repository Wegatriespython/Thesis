# Description: This file contains the implementation of the Firm class, which is a subclass of the Agent class in the Mesa library. The Firm class represents a firm in the model. The Firm class has two subclasses, Firm1 and Firm2, which represent two different types of firms in the model. The Firm class has the following attributes: capital, productivity, price, inventory, workers, demand, production, sales, budget, RD_investment, and expected_demand. The Firm class has the following methods: step, produce, cobb_douglas_production, adjust_price, calculate_marginal_cost, and calculate_expected_demand. The Firm1 class is a subclass of the Firm class and has the following attributes: inventory. The Firm1 class has the following methods: step and innovate. The Firm2 class is a subclass of the Firm
from mesa import Agent
import random

class Firm(Agent):
    def __init__(self, unique_id, model, initial_capital, initial_rd_investment):
        super().__init__(unique_id, model)
        self.capital = initial_capital
        self.productivity = model.config.INITIAL_PRODUCTIVITY
        self.price = model.config.INITIAL_PRICE
        self.inventory = model.config.INITIAL_INVENTORY
        self.workers = []
        self.demand = model.config.INITIAL_DEMAND
        self.production = 0
        self.sales = 0
        self.budget = 0
        self.RD_investment = initial_rd_investment
        self.expected_demand = model.config.INITIAL_DEMAND

    def step(self):
        self.produce()
        self.adjust_price()

    def produce(self):
        if self.inventory < self.model.config.INVENTORY_THRESHOLD:
            self.production = self.cobb_douglas_production()
            self.production = max(0, min(self.production, self.expected_demand - self.inventory))
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

    def calculate_expected_demand(self, average_market_demand):
        self.expected_demand = self.model.config.DEMAND_ADJUSTMENT_RATE * average_market_demand + (1 - self.model.config.DEMAND_ADJUSTMENT_RATE) * self.demand
        self.demand = self.expected_demand

class Firm1(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM1_INITIAL_CAPITAL, model.config.FIRM1_INITIAL_RD_INVESTMENT)
        self.inventory = model.config.INITIAL_INVENTORY  # Explicitly initialize inventory

    def step(self):
        self.innovate()
        super().step()
        self.inventory += self.production  # Update inventory after production

    def innovate(self):
        if random.random() < self.model.config.INNOVATION_ATTEMPT_PROBABILITY:
            self.RD_investment = self.capital * self.model.config.FIRM1_RD_INVESTMENT_RATE
            if random.random() < self.model.config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity *= (1 + self.model.config.PRODUCTIVITY_INCREASE)

class Firm2(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM2_INITIAL_CAPITAL, model.config.FIRM2_INITIAL_INVESTMENT_DEMAND)
        self.investment_demand = model.config.FIRM2_INITIAL_INVESTMENT_DEMAND
        self.investment = 0
        self.desired_capital = model.config.FIRM2_INITIAL_DESIRED_CAPITAL

    def step(self):
        self.calculate_investment_demand()
        super().step()

    def calculate_investment_demand(self):
        if self.demand > 0 and len(self.workers) > 0:
            self.desired_capital = (self.demand / (self.model.config.TOTAL_FACTOR_PRODUCTIVITY * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY)))) ** (1 / self.model.config.CAPITAL_ELASTICITY)
            self.investment_demand = max(0, self.desired_capital - self.capital)
        else:
            self.investment_demand = 0