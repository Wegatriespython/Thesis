# In Accounting_System.py
from Config import config

class AccountingSystem:
    def __init__(self):
        self.assets = {'cash': 0, 'inventory': 0, 'capital': 0}
        self.liabilities = {}
        self.equity = {'retained_earnings': 0}
        self.income = {'sales': 0, 'capital_sales': 0}
        self.expenses = {'wages': 0, 'capital_purchases': 0}

    def record_transaction(self, from_account, to_account, amount):
        if from_account in self.assets:
            self.assets[from_account] -= amount
        elif from_account in self.expenses:
            self.expenses[from_account] += amount

        if to_account in self.assets:
            self.assets[to_account] += amount
        elif to_account in self.income:
            self.income[to_account] += amount

    def update_balance_sheet(self):
        total_assets = sum(self.assets.values())
        total_liabilities = sum(self.liabilities.values())
        self.equity['retained_earnings'] = total_assets - total_liabilities

    def record_income(self, account, amount):
        self.income[account] = self.income.get(account, 0) + amount

    def record_expense(self, account, amount):
        self.expenses[account] = self.expenses.get(account, 0) + amount

    def calculate_profit(self):
        return sum(self.income.values()) - sum(self.expenses.values())
    
    def get_total_demand(self):
        return self.assets.get('accounts_receivable', 0) + self.income.get('sales', 0)

    def get_total_production(self):
        return self.assets.get('inventory', 0) + self.income.get('sales', 0)

class GlobalAccountingSystem:
    def __init__(self):
        self.total_labor = config.INITIAL_WORKERS
        self.total_capital = (config.INITIAL_CAPITAL_FIRMS * config.FIRM1_INITIAL_CAPITAL + 
                              config.INITIAL_CONSUMPTION_FIRMS * config.FIRM2_INITIAL_CAPITAL)
        self.total_goods = (config.INITIAL_CAPITAL_FIRMS + config.INITIAL_CONSUMPTION_FIRMS) * config.INITIAL_INVENTORY
        self.total_money = (config.INITIAL_WORKERS * config.INITIAL_SAVINGS + 
                            (config.INITIAL_CAPITAL_FIRMS * config.FIRM1_INITIAL_CAPITAL + 
                             config.INITIAL_CONSUMPTION_FIRMS * config.FIRM2_INITIAL_CAPITAL))
        
        self.market_demand = [config.INITIAL_DEMAND]
        self.capital_prices = [max(1, config.INITIAL_PRICE)]
        self.wages = [max(1, config.INITIAL_WAGE)]
        self.consumption_good_prices = [max(1, config.INITIAL_PRICE)]
        
        self.firms = []
        self.last_capital_sellers = []
        self.last_labor_sellers = []
        self.last_consumption_sellers = []

    def record_labor_transaction(self, firm, worker, quantity, price):
        self.total_money += price * quantity
        self.wages.append(max(1, price))
        self.total_labor += quantity

    def record_capital_transaction(self, buyer, seller, quantity, price):
        self.total_capital += quantity
        self.capital_prices.append(max(1, price))
        self.total_money += price * quantity

    def record_consumption_transaction(self, buyer, seller, quantity, price):
        self.total_goods += quantity
        self.consumption_good_prices.append(max(1, price))
        self.total_money += price * quantity

    def record_market_demand(self, demand):
        self.market_demand.append(demand)

    def get_total_labor(self):
        return self.total_labor

    def get_total_capital(self):
        return self.total_capital

    def get_total_goods(self):
        return self.total_goods

    def get_total_money(self):
        return self.total_money

    def get_average_market_demand(self):
        return max(1, sum(self.market_demand) / len(self.market_demand) if self.market_demand else 0)
    
    def get_average_capital_price(self):
        if self.capital_prices:
            return max(1, sum(self.capital_prices) / len(self.capital_prices))
        elif self.last_capital_sellers:
            return max(1, sum(seller.price for seller in self.last_capital_sellers) / len(self.last_capital_sellers))
        return max(1, config.INITIAL_PRICE)

    def get_average_wage(self):
        if self.wages:
            return max(1, sum(self.wages) / len(self.wages))
        elif self.last_labor_sellers:
            return max(1, sum(seller.wage for seller in self.last_labor_sellers) / len(self.last_labor_sellers))
        return max(1, config.INITIAL_WAGE)

    def get_average_consumption_good_price(self):
        if self.consumption_good_prices:
            return max(1, sum(self.consumption_good_prices) / len(self.consumption_good_prices))
        elif self.last_consumption_sellers:
            return max(1, sum(seller.price for seller in self.last_consumption_sellers) / len(self.last_consumption_sellers))
        return max(1, config.INITIAL_PRICE)

    
    def register_firm(self, firm):
        self.firms.append(firm)

    def get_total_demand(self):
        return sum(firm.accounts.get_total_demand() for firm in self.firms)

    def get_total_production(self):
        return sum(firm.accounts.get_total_production() for firm in self.firms)

    def check_consistency(self):
        total_assets = self.total_capital + self.total_goods + self.total_money
        total_liabilities_and_equity = self.calculate_total_liabilities_and_equity()
        assert abs(total_assets - total_liabilities_and_equity) < 1e-6, "Balance sheet inconsistency detected"

    def calculate_total_liabilities_and_equity(self):
        return self.total_capital + self.total_goods + self.total_money

    def reset_period_data(self):
        self.market_demand = [self.get_average_market_demand()]
        self.capital_prices = []
        self.wages = []
        self.consumption_good_prices = []
        self.last_capital_sellers = []
        self.last_labor_sellers = []
        self.last_consumption_sellers = []

    def update_sellers(self, capital_sellers, labor_sellers, consumption_sellers):
        self.last_capital_sellers = capital_sellers
        self.last_labor_sellers = labor_sellers
        self.last_consumption_sellers = consumption_sellers

    # Adding missing methods based on the error message and potential needs
    def update_average_wage(self):
        if self.wages:
            self.wages = [self.get_average_wage()]

    def update_average_capital_price(self):
        if self.capital_prices:
            self.capital_prices = [self.get_average_capital_price()]

    def update_average_consumption_good_price(self):
        if self.consumption_good_prices:
            self.consumption_good_prices = [self.get_average_consumption_good_price()]

    # Additional methods that might be needed based on common economic model requirements
    def get_unemployment_rate(self):
        employed = sum(len(firm.workers) for firm in self.firms)
        return max(0, (self.total_labor - employed) / self.total_labor) if self.total_labor > 0 else 0

    def get_gdp(self):
        return self.get_total_production() * self.get_average_consumption_good_price()

    def get_inflation_rate(self):
        if len(self.consumption_good_prices) > 1:
            previous_price = self.consumption_good_prices[-2]
            current_price = self.consumption_good_prices[-1]
            return (current_price - previous_price) / previous_price if previous_price > 0 else 0
        return 0

    def get_capital_utilization(self):
        total_capacity = sum(firm.capital for firm in self.firms)
        return self.get_total_production() / total_capacity if total_capacity > 0 else 0
