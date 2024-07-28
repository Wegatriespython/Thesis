from mesa import Agent

class AccountingSystem:
    def __init__(self):
        self.assets = {}
        self.liabilities = {}
        self.equity = {}
        self.income = {}
        self.expenses = {}

    def record_transaction(self, from_account, to_account, amount):
        self.assets[from_account] = self.assets.get(from_account, 0) - amount
        self.assets[to_account] = self.assets.get(to_account, 0) + amount

    def update_balance_sheet(self):
        self.equity['retained_earnings'] = sum(self.assets.values()) - sum(self.liabilities.values())

    def record_income(self, account, amount):
        self.income[account] = self.income.get(account, 0) + amount

    def record_expense(self, account, amount):
        self.expenses[account] = self.expenses.get(account, 0) + amount

    def calculate_profit(self):
        return sum(self.income.values()) - sum(self.expenses.values())

# Usage in Firm class
class Firm(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.accounts = AccountingSystem()

    def sell_goods(self, quantity, price):
        revenue = quantity * price
        self.accounts.record_income('sales', revenue)
        self.accounts.record_transaction('inventory', 'cash', revenue)

    def pay_wages(self, amount):
        self.accounts.record_expense('wages', amount)
        self.accounts.record_transaction('cash', 'wages_payable', amount)