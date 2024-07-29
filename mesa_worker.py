from mesa import Agent
from Accounting_System import AccountingSystem
from utility_function import worker_decision
import numpy as np

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
        self.wage_history = [model.config.MINIMUM_WAGE] * 5  # Initialize with minimum wage
        self.expected_wage = model.config.MINIMUM_WAGE
        self.historic_price = model.config.INITIAL_PRICE  # Add this line
        self.price_history = [model.config.INITIAL_PRICE]  # Add this line

    def step(self):
        self.update_expected_wage()
        self.make_economic_decision()
        self.update_skills()
        self.update_historic_price()  # Add this method call


    def update_historic_price(self):
        current_price = self.model.global_accounting.get_average_consumption_good_price()
        self.price_history.append(current_price)
        if len(self.price_history) > 10:  # Keep only last 10 periods
            self.price_history.pop(0)
        self.historic_price = sum(self.price_history) / len(self.price_history)
    def update_expected_wage(self):
        if self.employed:
            self.wage_history.append(self.wage)
        else:
            self.wage_history.append(0)  # Represent unemployment with 0 wage
        
        self.wage_history = self.wage_history[-5:]  # Keep only the last 5 periods
        self.expected_wage = max(np.mean(self.wage_history), self.model.config.MINIMUM_WAGE)

    def make_economic_decision(self):
        
        current_price = max(self.model.global_accounting.get_average_consumption_good_price(), 1)
        optimal_consumption, max_acceptable_price, desired_wage = worker_decision(
            self.savings, self.wage, self.model.global_accounting.get_average_wage(),
            self.model.global_accounting.get_average_consumption_good_price(),
            self.historic_price
        )
        
        self.consumption = optimal_consumption
        self.price = max_acceptable_price
        self.wage = desired_wage

    def update_skills(self):
        if self.employed:
            self.skills *= (1 + self.model.config.SKILL_GROWTH_RATE)
        else:
            self.skills *= (1 - self.model.config.SKILL_DECAY_RATE)

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
        return self.price

    def update_after_markets(self):
        self.accounts.update_balance_sheet()
        if self.employed:
            self.savings += self.wage
        self.savings -= self.consumption * self.model.global_accounting.get_average_consumption_good_price()