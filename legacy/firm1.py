from legacy.Basefirm import BaseFirm
from Config import config
import random

class Firm1(BaseFirm):
    def __init__(self):
        super().__init__()
        self.capital = config.FIRM1_INITIAL_CAPITAL
        self.RD_investment = config.FIRM1_INITIAL_RD_INVESTMENT
        self.inventory_threshold = config.FIRM1_INVENTORY_THRESHOLD
        self.innovation_success_count = 0
        self.productivity_increase_count = 0
        

    def innovate(self):
        if random.random() < config.INNOVATION_ATTEMPT_PROBABILITY:
            self.innovation_success_count += 1
            self.RD_investment = self.capital * config.FIRM1_RD_INVESTMENT_RATE
            
            if random.random() < config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity_increase_count += 1
                self.productivity *= (1 + config.PRODUCTIVITY_INCREASE)
                
        print(f"Firm1 {id(self)} - Innovation attempts: {self.innovation_success_count}, Productivity increases: {self.productivity_increase_count}")

    def update_state(self):
        super().update_state()
 