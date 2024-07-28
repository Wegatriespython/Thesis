# firm2.py
from legacy.Basefirm import BaseFirm
from Config import config
import math

class Firm2(BaseFirm):
    def __init__(self):
        super().__init__()
        self.capital = config.FIRM2_INITIAL_CAPITAL
        self.investment_demand = 0
        self.investment = 0
        self.desired_capital = 0

    def calculate_investment_demand(self):
        # Calculate desired capital using Cobb-Douglas production function
        if self.demand > 0 and len(self.workers) > 0:
            self.desired_capital = (self.demand / (self.total_factor_productivity * (len(self.workers) ** (1 - self.capital_elasticity)))) ** (1 / self.capital_elasticity)
            self.investment_demand = max(0, self.desired_capital - self.capital)
        else:
            self.investment_demand = 0

    def update_state(self):
        super().update_state()
        self.calculate_investment_demand()

    def receive_capital(self, capital_amount):
        self.capital += capital_amount
        self.investment = capital_amount
        self.investment_demand = max(0, self.investment_demand - capital_amount)

