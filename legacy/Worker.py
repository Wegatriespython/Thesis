# Worker.py
from Config import config
import random
import math
from legacy.Wageoffer import WageOffer

class Worker:
    def __init__(self):
        self.employed = False
        self.employer = None
        self.wage = config.INITIAL_WAGE
        self.savings = config.INITIAL_SAVINGS
        self.skills = config.INITIAL_SKILLS
        self.offers = []
        self.consumption = config.INITIAL_CONSUMPTION
        self.satiated = False

    def update_state(self):
        if self.consumption > 0: 
            self.consumption = 0

    def update_skills(self):
        if self.employed:
            new_skills = self.skills * (1 + config.SKILL_GROWTH_RATE)
        else:
            new_skills = self.skills * (1 - config.SKILL_DECAY_RATE)
        return [(self, 'skills', new_skills)]

    def apply_for_jobs(self, firms):
        self.offers = []
        for firm in firms:
            wage = firm.get_wage_offer(self)
            self.offers.append(WageOffer(self, firm, wage))

    def calculate_desired_consumption(self):
        return min(self.wage * config.CONSUMPTION_PROPENSITY, self.savings)

    def purchase_goods(self, quantity, price):
        cost = quantity * price
        if self.savings >= cost:
            self.savings -= cost
            self.consumption += quantity
            return True
        return False