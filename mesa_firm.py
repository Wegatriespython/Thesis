from mesa import Agent
import numpy as np
import random
from Simple_profit_maxxing import simple_profit_maximization
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
        self.labor_demand = 0
        self.investment_demand = 0

    def step(self):
        self.optimize_production()
        self.produce()

    def optimize_production(self):
        optimal_labor, optimal_capital, optimal_price, optimal_production =   simple_profit_maximization(
            self.budget, self.capital, len(self.workers), self.price, self.productivity,
            self.calculate_expected_demand(), self.model.get_average_wage(), self.model.get_average_capital_price(), self.model.config.CAPITAL_ELASTICITY)
        self.adjust_labor(optimal_labor)
        self.adjust_capital(optimal_capital)
        self.price = optimal_price
        self.production = optimal_production

    def adjust_labor(self, optimal_labor):
        current_labor = len(self.workers)
        if optimal_labor > current_labor:
            self.labor_demand = optimal_labor - current_labor
        elif optimal_labor < current_labor:
            workers_to_fire = current_labor - optimal_labor
            for _ in range(int(workers_to_fire)):
                if self.workers:
                    worker = self.workers.pop()
                    worker.employed = False
                    worker.employer = None
                    worker.wage = 0
        else:
            self.labor_demand = 0

    def adjust_capital(self, optimal_capital):
        capital_difference = optimal_capital - self.capital
        if capital_difference > 0:
            capital_to_buy = min(capital_difference, self.budget // self.model.get_average_capital_price())
            self.investment_demand = capital_to_buy
        elif capital_difference < 0:
            self.investment_demand = 0

    def produce(self):
        self.inventory += self.production

    def calculate_expected_demand(self):
        return self.model.config.DEMAND_ADJUSTMENT_RATE * self.model.average_market_demand + (1 - self.model.config.DEMAND_ADJUSTMENT_RATE) * self.demand

    def cobb_douglas_production(self, labor, capital):
        return self.productivity * (capital ** self.model.config.CAPITAL_ELASTICITY) * (labor ** (1 - self.model.config.CAPITAL_ELASTICITY))

class Firm1(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM1_INITIAL_CAPITAL, model.config.FIRM1_INITIAL_RD_INVESTMENT)

    def step(self):
        self.innovate()
        super().step()

    def innovate(self):
        if random.random() < self.model.config.INNOVATION_ATTEMPT_PROBABILITY:
            self.RD_investment = self.capital * self.model.config.FIRM1_RD_INVESTMENT_RATE
            self.budget -= self.RD_investment
            if random.random() < self.model.config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity *= (1 + self.model.config.PRODUCTIVITY_INCREASE)

class Firm2(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM2_INITIAL_CAPITAL, model.config.FIRM2_INITIAL_INVESTMENT_DEMAND)
        self.investment_demand = model.config.FIRM2_INITIAL_INVESTMENT_DEMAND
        self.investment = 0
        self.desired_capital = model.config.FIRM2_INITIAL_DESIRED_CAPITAL