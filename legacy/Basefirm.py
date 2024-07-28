from Config import config
import random

class BaseFirm:
    def __init__(self):
        self.capital = config.INITIAL_CAPITAL
        self.productivity = config.INITIAL_PRODUCTIVITY
        self.price = 1
        self.inventory = config.INITIAL_INVENTORY
        self.workers = []
        self.demand = config.INITIAL_DEMAND
        self.production = 0
        self.sales = 0
        self.desired_workers = 1
        self.quantity_sold = 0
        self.budget = 0
        self.profit = 0
        self.sell_orders = []
        self.total_factor_productivity = config.TOTAL_FACTOR_PRODUCTIVITY
        self.capital_elasticity = config.CAPITAL_ELASTICITY
        self.markup_rate = config.MARKUP_RATE
        self.wage_offers = []

    def calculate_profit(self):
        revenue = self.sales * self.price
        labor_cost = sum(worker.wage for worker in self.workers)
        capital_cost = self.capital * config.CAPITAL_RENTAL_RATE
        self.profit = revenue - labor_cost - capital_cost
        return self.profit

    def adjust_workforce(self):
        L = max(len(self.workers), 0.1)  # Avoid division by zero
        MPL = (1 - self.capital_elasticity) * self.total_factor_productivity * (self.capital ** self.capital_elasticity) * (L ** (-self.capital_elasticity))
        workers_for_demand = (self.demand / self.total_factor_productivity / (self.capital ** self.capital_elasticity)) ** (1 / (1 - self.capital_elasticity))

        if self.inventory > config.INVENTORY_THRESHOLD:
            self.desired_workers = max(1, int(self.desired_workers * 0.95))
        elif self.demand > self.production:
            self.desired_workers = min(self.desired_workers, int(workers_for_demand))

    def produce(self):
        if self.inventory < config.INVENTORY_THRESHOLD:
            self.production = self.cobb_douglas_production()
            self.production = max(0, min(self.production, self.demand - self.inventory))
            self.inventory += self.production
        else:
            self.production = 0

    def cobb_douglas_production(self):
        return self.total_factor_productivity * (self.capital ** self.capital_elasticity) * (len(self.workers) ** (1 - self.capital_elasticity))
            
    def adjust_price(self):
        marginal_cost = self.calculate_marginal_cost()
        self.price = max(1, (1 + self.markup_rate) * marginal_cost)

    def add_sell_order(self, buyer, quantity, price):
        self.sell_orders.append((buyer, quantity, price))

    def clear_orders(self):
        self.sell_orders.clear()
        
    def calculate_marginal_cost(self):
        if self.production > 0:
            return (sum(worker.wage for worker in self.workers) + self.capital * config.CAPITAL_RENTAL_RATE) / self.production
        return 0

    def calculate_budget(self):
        self.budget = self.sales + self.capital - sum(worker.wage for worker in self.workers)
        return self.budget

    def update_state(self):
        self.calculate_budget()
        self.adjust_workforce()
        self.produce()
        self.adjust_price()
        self.manage_wage_offers()

    def get_wage_offer(self, worker):
        L = len(self.workers) + 1
        MPL = (1 - self.capital_elasticity) * self.total_factor_productivity * (self.capital ** self.capital_elasticity) * (L ** (-self.capital_elasticity))
        
        min_wage = config.MINIMUM_WAGE
        max_wage = MPL * (worker.skills if worker else 1)
        wage_offer = min_wage + (max_wage - min_wage) * random.random()
        
        return max(min_wage, min(wage_offer, max_wage))

    def calculate_expected_demand(self, average_consumption):
        beta = 0.7  # This is a smoothing factor. Adjust as needed.

        self.demand= beta*self.demand +(1-beta)* average_consumption  # Use actual sales as a proxy for realized demand
        
        self.demand = max(self.demand, config.MIN_DEMAND)  # Ensure demand doesn't fall below a minimum threshold



    def manage_wage_offers(self):
        self.wage_offers.clear()
        for _ in range(self.desired_workers - len(self.workers)):
            self.wage_offers.append(self.get_wage_offer(None))

    def fulfill_order(self, quantity):
        sold = min(quantity, self.inventory)
        self.inventory -= sold
        return sold
    
