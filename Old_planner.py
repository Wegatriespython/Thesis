from mesa_economy import EconomyModel
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2
import numpy as np
from scipy.optimize import minimize
class NashCentralPlanner:
def init(self, model: EconomyModel):
self.model = model
self.config = model.config
self.num_firms = self.model.num_firm1 + self.model.num_firm2
self.firms = [agent for agent in self.model.schedule.agents if isinstance(agent, (Firm1, Firm2))]
self.workers = [agent for agent in self.model.schedule.agents if isinstance(agent, Worker)]
self.firm1s = [firm for firm in self.firms if isinstance(firm, Firm1)]
self.firm2s = [firm for firm in self.firms if isinstance(firm, Firm2)]
def objective_function(self, x):
    labor_allocation, capital_allocation, wages, relative_price = self.unpack_decision_variables(x)

    total_welfare = self.calculate_total_welfare(labor_allocation, capital_allocation, wages, relative_price)

    labor_penalty = self.labor_market_penalty(labor_allocation)
    capital_penalty = self.capital_market_penalty(capital_allocation, labor_allocation)
    consumption_penalty = self.consumption_market_penalty(labor_allocation, capital_allocation, wages, relative_price)
    budget_penalty = self.budget_constraint_penalty(labor_allocation, capital_allocation, wages, relative_price)

    return -total_welfare + 1000 * (labor_penalty + capital_penalty + consumption_penalty + budget_penalty)

def unpack_decision_variables(self, x):
    labor_allocation = x[:self.num_firms]
    capital_allocation = x[self.num_firms:2*self.num_firms]
    wages = x[2*self.num_firms:3*self.num_firms]
    relative_price = x[-1]  # Price of capital goods relative to consumption goods (numeraire)
    return labor_allocation, capital_allocation, wages, relative_price

def calculate_total_welfare(self, labor_allocation, capital_allocation, wages, relative_price):
    total_welfare = 0
    for t in range(self.config.TIME_HORIZON):
        period_consumption = self.calculate_period_consumption(labor_allocation, capital_allocation)
        worker_income = sum(wages * labor_allocation)
        real_consumption = worker_income  # Since consumption good is numeraire
        period_welfare = np.log(max(real_consumption, 1e-6))
        total_welfare += period_welfare / (1 + self.config.DISCOUNT_RATE)**t
    return total_welfare

def calculate_period_consumption(self, labor_allocation, capital_allocation): # sus
    total_production = 0
    for i, firm in enumerate(self.firm2s):
        labor = labor_allocation[i + len(self.firm1s)]
        capital = capital_allocation[i + len(self.firm1s)]
        production = firm.productivity * (capital ** self.config.CAPITAL_ELASTICITY) * (labor ** (1 - self.config.CAPITAL_ELASTICITY))
        total_production += production
    return total_production

def labor_market_penalty(self, labor_allocation):
    total_labor_demand = sum(labor_allocation)
    total_labor_supply = self.model.num_workers
    return abs(total_labor_demand - total_labor_supply)

def capital_market_penalty(self, capital_allocation, labor_allocation):
    capital_production = sum(self.calculate_firm1_production(labor_allocation[:len(self.firm1s)],
                                                             capital_allocation[:len(self.firm1s)]))
    capital_demand = sum(capital_allocation[len(self.firm1s):])
    return abs(capital_production - capital_demand)

def consumption_market_penalty(self, labor_allocation, capital_allocation, wages, relative_price):
    total_production = self.calculate_period_consumption(labor_allocation, capital_allocation)
    worker_income = sum(wages * labor_allocation)
    total_consumption = worker_income  # Assuming workers spend all income on consumption
    return abs(total_production - total_consumption)

def budget_constraint_penalty(self, labor_allocation, capital_allocation, wages, relative_price):
    penalty = 0

    # Firm1 budget constraint
    for i, firm in enumerate(self.firm1s):
        labor_cost = wages[i] * labor_allocation[i]
        revenue = relative_price * self.calculate_firm1_production([labor_allocation[i]], [capital_allocation[i]])[0]
        if revenue < labor_cost:
            penalty += abs(revenue - labor_cost)

    # Firm2 budget constraint
    for i, firm in enumerate(self.firm2s):
        labor_cost = wages[i + len(self.firm1s)] * labor_allocation[i + len(self.firm1s)]
        capital_cost = relative_price * capital_allocation[i + len(self.firm1s)]
        revenue = self.calculate_firm2_production([labor_allocation[i + len(self.firm1s)]],
                                                  [capital_allocation[i + len(self.firm1s)]])[0]
        if revenue < labor_cost + capital_cost:
            penalty += abs(revenue - labor_cost - capital_cost)

    return penalty

def calculate_firm1_production(self, labor, capital):
    return [firm.productivity * (l ** (1 - self.config.CAPITAL_ELASTICITY)) * (k ** self.config.CAPITAL_ELASTICITY)
            for firm, l, k in zip(self.firm1s, labor, capital)]

def calculate_firm2_production(self, labor, capital):
    return [firm.productivity * (l ** (1 - self.config.CAPITAL_ELASTICITY)) * (k ** self.config.CAPITAL_ELASTICITY)
            for firm, l, k in zip(self.firm2s, labor, capital)]

def optimize(self):
    num_variables = 3 * self.num_firms + 1  # labor, capital, wages for each firm, plus relative price

    initial_guess = np.ones(num_variables)

    bounds = [(0, None) for _ in range(2 * self.num_firms)]  # Non-negative labor and capital
    bounds += [(self.config.MINIMUM_WAGE, None) for _ in range(self.num_firms)]  # Minimum wage constraint
    bounds += [(0.1, 10)]  # Relative price bounds

    constraints = ({'type': 'eq', 'fun': lambda x: sum(x[:self.num_firms]) - len(self.workers)})  # Labor market clearing

    result = minimize(self.objective_function, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    labor_allocation, capital_allocation, wages, relative_price = self.unpack_decision_variables(result.x)

    return {
        'labor_allocation': labor_allocation,
        'capital_allocation': capital_allocation,
        'wages': wages,
        'relative_price': relative_price
    }


def apply_decisions(self, decisions):
    labor_allocation = decisions['labor_allocation']
    capital_allocation = decisions['capital_allocation']
    wages = decisions['wages']
    relative_price = decisions['relative_price']

    # Update firms
    for i, firm in enumerate(self.firms):
        firm.apply_central_decision(labor_allocation[i], capital_allocation[i], wages[i])
        if isinstance(firm, Firm1):
            firm.price = relative_price  # Price relative to consumption good (numeraire)
        else:
            firm.price = 1  # Consumption good is numeraire

    # Update workers
    total_labor = sum(labor_allocation)
    employed_workers = np.random.choice(self.workers, size=int(total_labor), replace=False)
    for worker in self.workers:
        if worker in employed_workers:
            worker.apply_central_decision(True, np.mean(wages), worker.consumption)
        else:
            worker.apply_central_decision(False, 0, worker.consumption)

    # Update model's relative price
    self.model.relative_price = relative_price
def update_model(self, optimal_solution):
    labor_allocation = optimal_solution['labor_allocation']
    capital_allocation = optimal_solution['capital_allocation']
    wages = optimal_solution['wages']
    relative_price = optimal_solution['relative_price']

    # Update firms
    for i, firm in enumerate(self.firms):
        firm.labor_demand = labor_allocation[i]
        firm.capital = capital_allocation[i]
        firm.wage = wages[i]
        if isinstance(firm, Firm1):
            firm.price = relative_price  # Price relative to consumption good (numeraire)
        else:
            firm.price = 1  # Consumption good is numeraire

        if isinstance(firm, Firm1):
            firm.production = self.calculate_firm1_production([labor_allocation[i]], [capital_allocation[i]])[0]
        else:
            firm.production = self.calculate_firm2_production([labor_allocation[i]], [capital_allocation[i]])[0]

        firm.inventory += firm.production

    # Update workers
    total_labor = sum(labor_allocation)
    for worker in self.workers:
        if total_labor > 0:
            worker.employed = True
            worker.wage = np.mean(wages)
            worker.savings += worker.wage
        else:
            worker.employed = False
            worker.wage = 0

    # Update global accounting
    self.model.global_accounting.update_market_demand(sum(firm.production for firm in self.firm2s))

    # Update model's relative price
    self.model.relative_price = relative_price

def run_simulation(self, steps):
    for step in range(steps):
        optimal_solution = self.optimize()
        self.update_model(optimal_solution)
        self.print_solution(step, optimal_solution)

def print_solution(self, step, optimal_solution):
    labor_allocation = optimal_solution['labor_allocation']
    capital_allocation = optimal_solution['capital_allocation']
    wages = optimal_solution['wages']
    relative_price = optimal_solution['relative_price']

    print(f"\n--- Step {step} ---")
    print("Labor Allocation:")
    for i, labor in enumerate(labor_allocation):
        print(f"  Firm {i}: {labor:.2f}")

    print("\nCapital Allocation:")
    for i, capital in enumerate(capital_allocation):
        print(f"  Firm {i}: {capital:.2f}")

    print("\nWages:")
    for i, wage in enumerate(wages):
        print(f"  Firm {i}: {wage:.2f}")

    print(f"\nRelative Price (Capital/Consumption): {relative_price:.2f}")

    total_production = self.calculate_period_consumption(labor_allocation, capital_allocation)
    print(f"\nTotal Consumption Good Production: {total_production:.2f}")

    total_capital_production = sum(self.calculate_firm1_production(labor_allocation[:len(self.firm1s)],
                                                                capital_allocation[:len(self.firm1s)]))
    print(f"Total Capital Good Production: {total_capital_production:.2f}")

    total_welfare = self.calculate_total_welfare(labor_allocation, capital_allocation, wages, relative_price)
    print(f"Total Welfare: {total_welfare:.2f}")

    labor_penalty = self.labor_market_penalty(labor_allocation)
    capital_penalty = self.capital_market_penalty(capital_allocation, labor_allocation)
    consumption_penalty = self.consumption_market_penalty(labor_allocation, capital_allocation, wages, relative_price)
    budget_penalty = self.budget_constraint_penalty(labor_allocation, capital_allocation, wages, relative_price)
    print(f"Penalties - Labor: {labor_penalty:.2f}, Capital: {capital_penalty:.2f}, "
        f"Consumption: {consumption_penalty:.2f}, Budget: {budget_penalty:.2f}")

economy_model = EconomyModel(num_workers=100, num_firm1=5, num_firm2=5,mode='centralized')
planner = NashCentralPlanner(economy_model)
planner.run_simulation(steps=50)