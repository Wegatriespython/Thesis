# Description: This file contains the Worker class, which is a subclass of the Agent class from the mesa library. The Worker class represents a worker agent in the model. Each worker has a unique ID, a boolean employed, an employer, a wage, savings, skills, consumption, and a boolean satiated. The Worker class has a step method that updates the worker's skills and a calculate_desired_consumption method that calculates the worker's desired consumption based on their wage and savings. The Worker class is used in the model to represent workers in the labor market.
from mesa import Agent
from Config import Config

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