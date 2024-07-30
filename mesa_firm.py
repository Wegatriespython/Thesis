from mesa import Agent
from Simple_profit_maxxing import neoclassical_profit_maximization
from Accounting_System import AccountingSystem

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
        self.inventory_value = self.inventory * self.price
        self.budget = self.capital + self.inventory_value
        self.RD_investment = initial_rd_investment
        self.labor_demand = 0
        self.investment_demand = 0
        self.accounts = AccountingSystem()
        self.historic_sales = []
        self.price_adjustment_factor = model.config.PRICE_ADJUSTMENT_FACTOR
        self.expected_periods = model.config.EXPECTED_PERIODS
        self.discount_rate = model.config.DISCOUNT_RATE
        print(f"Firm {unique_id} initialized:")
        print(f"  Capital: {self.capital}")
        print(f"  Productivity: {self.productivity}")
        print(f"  Price: {self.price}")
        print(f"  Inventory: {self.inventory}")

    def step(self):
        self.depreciate_inventory()
        self.optimize_production()
        self.produce()
        self.update_historic_sales()
        print(f"Firm {self.unique_id} decision - Labor Demand: {self.labor_demand}, Investment Demand: {self.investment_demand}, Production: {self.production}")

    def depreciate_inventory(self):
        if self.inventory > 0:
            depreciation_amount = self.inventory * self.model.config.DEPRECIATION_RATE
            self.inventory = max(0, self.inventory - depreciation_amount)
            old_inventory_value = self.inventory_value
            self.inventory_value = self.inventory * self.price
            value_loss = old_inventory_value - self.inventory_value
            self.budget -= value_loss
            self.accounts.record_expense('inventory_depreciation', value_loss)
            print(f"Firm {self.unique_id} depreciated inventory by {depreciation_amount:.2f} units, value loss: {value_loss:.2f}")
        else:
            print(f"Firm {self.unique_id} has no inventory to depreciate.")
        
    def optimize_production(self):
        try:
            optimal_labor, optimal_capital, optimal_price, optimal_production = neoclassical_profit_maximization(
                self.budget, self.capital, len(self.workers), self.price, self.productivity,
                self.calculate_expected_demand(), self.model.global_accounting.get_average_wage(), 
                self.model.global_accounting.get_average_capital_price(), self.model.config.CAPITAL_ELASTICITY,
                self.inventory, self.model.config.DEPRECIATION_RATE, self.price_adjustment_factor,
                self.expected_periods, self.discount_rate, self.historic_sales)
            
            self.adjust_labor(optimal_labor)
            self.adjust_capital(optimal_capital)
            self.price = optimal_price
            self.production = optimal_production
        except ValueError as e:
            print(f"Optimization failed for Firm {self.unique_id}: {str(e)}")
            # Fallback strategy: maintain current levels
            self.production = self.calculate_production()

    def adjust_labor(self, optimal_labor):
        current_labor = len(self.workers)
        if optimal_labor > current_labor:
            self.labor_demand = optimal_labor - current_labor
        elif optimal_labor < current_labor:
            self.fire_workers(int(current_labor - optimal_labor))
        else:
            self.labor_demand = 0

    def adjust_capital(self, optimal_capital):
        capital_difference = optimal_capital - self.capital
        if capital_difference > 0:
            self.investment_demand = min(capital_difference, self.budget // max(1,self.model.global_accounting.get_average_capital_price()))
        else:
            self.investment_demand = 0

    def produce(self):
        self.inventory += self.production

    def calculate_expected_demand(self):
        if not self.historic_sales:
            return self.model.global_accounting.get_average_market_demand()
        avg_historic_sales = sum(self.historic_sales) / len(self.historic_sales)
        return (self.model.config.DEMAND_ADJUSTMENT_RATE * self.model.global_accounting.get_average_market_demand() + 
                (1 - self.model.config.DEMAND_ADJUSTMENT_RATE) * avg_historic_sales)

    def update_historic_sales(self):
        self.historic_sales.append(self.sales)
        if len(self.historic_sales) > 10:  # Keep only last 10 periods
            self.historic_sales.pop(0)

    def hire_worker(self, worker, wage):
        self.workers.append(worker)
        self.budget -= wage
        self.labor_demand -= 1
        self.accounts.record_expense('wages', wage)

    def fire_workers(self, num_workers):
        for _ in range(num_workers):
            if self.workers:
                worker = self.workers.pop()
                worker.get_fired()

    def buy_capital(self, quantity, price):
        self.capital += quantity
        self.investment_demand -= quantity
        self.budget -= quantity * price
        self.accounts.record_transaction('cash', 'capital', quantity * price)

    def sell_capital(self, quantity, price):
        self.inventory -= quantity
        self.sales += quantity
        self.budget += quantity * price
        self.accounts.record_income('capital_sales', quantity * price)

    def sell_consumption_goods(self, quantity, price):
        self.inventory -= quantity
        self.sales += quantity
        self.budget += quantity * price
        self.accounts.record_income('consumption_sales', quantity * price)

    def update_after_markets(self):
        self.demand = self.sales
        self.sales = 0
        self.accounts.update_balance_sheet()

    def get_max_wage(self):
        return self.budget / self.labor_demand if self.labor_demand > 0 else 0

    def get_max_capital_price(self):
        return self.budget / self.investment_demand if self.investment_demand > 0 else 0

    def calculate_production(self):
        return self.productivity * (self.capital ** self.model.config.CAPITAL_ELASTICITY) * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY))

class Firm1(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM1_INITIAL_CAPITAL, model.config.FIRM1_INITIAL_RD_INVESTMENT)

    def step(self):
        self.innovate()
        super().step()

    def innovate(self):
        if self.model.random.random() < self.model.config.INNOVATION_ATTEMPT_PROBABILITY:
            self.RD_investment = self.capital * self.model.config.FIRM1_RD_INVESTMENT_RATE
            self.budget -= self.RD_investment
            if self.model.random.random() < self.model.config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity *= (1 + self.model.config.PRODUCTIVITY_INCREASE)

class Firm2(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM2_INITIAL_CAPITAL, model.config.FIRM2_INITIAL_INVESTMENT_DEMAND)
        self.investment = 0
        self.desired_capital = model.config.FIRM2_INITIAL_DESIRED_CAPITAL