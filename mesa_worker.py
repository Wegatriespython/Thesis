# mesa_worker.py

from mesa import Agent
from Accounting_System import AccountingSystem

class Worker(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.employed = False
        self.employer = None
        self.wage = model.config.INITIAL_WAGE
        self.savings = model.config.INITIAL_SAVINGS
        self.skills = model.config.INITIAL_SKILLS
        self.consumption = model.config.INITIAL_CONSUMPTION
        self.satiated = False
        self.accounts = AccountingSystem()

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

    def get_hired(self, employer, wage):
        self.employed = True
        self.employer = employer
        self.wage = wage
        self.accounts.record_income('wages', wage)

    def get_fired(self):
        self.employed = False
        self.employer = None
        self.wage = 0

    def consume(self, quantity, price):
        total_cost = quantity * price
        self.consumption += quantity
        self.savings -= total_cost
        self.accounts.record_expense('consumption', total_cost)

    def get_min_wage(self):
        return max(self.model.config.MINIMUM_WAGE, self.wage * (1 - self.model.config.WAGE_ADJUSTMENT_RATE))

    def get_max_consumption_price(self):
        desired_consumption = self.calculate_desired_consumption()
        return self.savings / desired_consumption if desired_consumption > 0 else 0

    def update_after_markets(self):
        self.accounts.update_balance_sheet()