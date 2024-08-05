class GlobalAccountingSystem:
    def __init__(self):
        self.total_labor = 0
        self.total_capital = 0
        self.total_goods = 0
        self.total_money = 0
        self.market_demand = []
        self.capital_prices = []
        self.wages = []
        self.consumption_good_prices = []
        self.firms = []
        self.relative_price_capital = 1.0
        self.relative_price_labor = 1.0

    def register_firm(self, firm):
        self.firms.append(firm)

    def get_total_demand(self):
        return sum(firm.expected_demand for firm in self.firms)

    def get_total_production(self):
        return sum(firm.production for firm in self.firms)

    def get_average_market_demand(self):
        return sum(self.market_demand) / len(self.market_demand) if self.market_demand else 0

    def get_average_capital_price(self):
        if not self.capital_prices or self.relative_price_capital == 0:
            return 0
        return (sum(self.capital_prices) / len(self.capital_prices)) / self.relative_price_capital


    def get_average_wage(self):
        if not self.wages or self.relative_price_labor == 0:
            return 0
        return (sum(self.wages) / len(self.wages)) / self.relative_price_labor

    def get_average_consumption_good_price(self):
        return sum(self.consumption_good_prices) / len(self.consumption_good_prices) if self.consumption_good_prices else 0

    def record_labor_transaction(self, firm, worker, quantity, price):
        self.total_labor += quantity
        self.wages.append(price * self.relative_price_labor)

    def record_capital_transaction(self, buyer, seller, quantity, price):
        self.total_capital += quantity
        self.capital_prices.append(price * self.relative_price_capital)

    def record_consumption_transaction(self, buyer, seller, quantity, price):
        self.total_goods += quantity
        self.consumption_good_prices.append(price)

    def update_market_demand(self, demand):
        self.market_demand.append(demand)
    def update_relative_prices(self, relative_price_capital, relative_price_labor):
        self.relative_price_capital = max(relative_price_capital, 1e-10)  # Prevent division by zero
        self.relative_price_labor = max(relative_price_labor, 1e-10)  # Prevent division by zero
    def reset_period_data(self):
        self.market_demand = []
        self.capital_prices = []
        self.wages = []
        self.consumption_good_prices = []

    def check_consistency(self):
        # Implement consistency checks if needed
        pass
