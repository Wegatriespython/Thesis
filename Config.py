#test Disables

class Config:
    def __init__(self):
        # Common parameters
        self.INITIAL_CAPITAL = 10
        self.INITIAL_PRODUCTIVITY = 1
        self.INITIAL_PRICE = 1
        self.INITIAL_WAGE = 1
        self.MAX_MPL = 100
        self.INITIAL_INVENTORY = 20
        self.INITIAL_DEMAND = 1
        self.MIN_DEMAND = 1
        self.INITIAL_SKILLS = .1
        self.DEMAND_ADJUSTMENT_RATE = 0.5 
        self.MARKUP_RATE = 0.2
        self.INITIAL_SAVINGS = 100
        self.MIN_CONSUMPTION = 1
        self.PRODUCTION_FACTOR = 0.1
        self.WAGE_OFFER_FACTOR = 1.1
        self.JOB_LOSS_PROBABILITY = 0.05
        self.MINIMUM_WAGE = 1
        self.CONSUMPTION_PROPENSITY =1
        self.INITIAL_CONSUMPTION = 0
        self.TOTAL_FACTOR_PRODUCTIVITY = 1.0
        self.CAPITAL_ELASTICITY = 0.3
        self.CAPITAL_RENTAL_RATE = 0.05
        self.SKILL_GROWTH_RATE = 0.01
        self.SKILL_DECAY_RATE = 0.005
        self.INVENTORY_THRESHOLD =20 
        # Firm1 specific parameters
        self.FIRM1_INITIAL_CAPITAL = 20
        self.FIRM1_INITIAL_RD_INVESTMENT = 0
        self.FIRM1_RD_INVESTMENT_RATE = 0.1
        self.FIRM1_INVENTORY_THRESHOLD = 10
        self.INNOVATION_ATTEMPT_PROBABILITY = 0.1  # Probability of a successful innovation attempt
        self.PRODUCTIVITY_INCREASE_PROBABILITY = 0.5  # Probability that a successful innovation increases productivity
        self.PRODUCTIVITY_INCREASE = 0.005  # Reduced from 0.1 to 0.05 for more gradual growth
        
        # Firm2 specific parameters
        self.FIRM2_INITIAL_CAPITAL = 5
        self.FIRM2_INITIAL_INVESTMENT = 0
        self.FIRM2_INITIAL_INVESTMENT_DEMAND = 10
        self.FIRM2_INITIAL_DESIRED_CAPITAL = 5
        self.FIRM2_MACHINE_OUTPUT_PER_PERIOD = 10
        self.FIRM2_INVENTORY_THRESHOLD = 20

        # Simulation parameters
        self.INITIAL_WORKERS = 20
        self.INITIAL_CAPITAL_FIRMS = 2  # This was previously INITIAL_FIRM1S
        self.INITIAL_CONSUMPTION_FIRMS = 5  # This was previously INITIAL_FIRM2S
        self.SIMULATION_STEPS = 10

# Create a global configuration object
config = Config()