import numpy as np
from pyomo.environ import *
import time
from mesa_economy import EconomyModel
from mesa_worker import Worker
from mesa_firm import Firm1, Firm2

class DynamicCentralPlanner:
    def __init__(self, model: EconomyModel):
        self.model = model
        self.config = model.config
        self.num_firms = self.model.num_firm1 + self.model.num_firm2
        self.firms = [agent for agent in self.model.schedule.agents if isinstance(agent, (Firm1, Firm2))]
        self.workers = [agent for agent in self.model.schedule.agents if isinstance(agent, Worker)]
        self.firm1s = [firm for firm in self.firms if isinstance(firm, Firm1)]
        self.firm2s = [firm for firm in self.firms if isinstance(firm, Firm2)]

    def optimize(self):
        model = ConcreteModel()

        # Define sets
        model.T = RangeSet(1, self.config.TIME_HORIZON)
        model.Firms = RangeSet(1, self.num_firms)

        # Define parameters
        model.discount_rate = Param(initialize=self.config.DISCOUNT_RATE)
        model.capital_elasticity = Param(initialize=self.config.CAPITAL_ELASTICITY)
        model.num_workers = Param(initialize=self.model.num_workers)

        # Define variables
        model.labor_allocation = Var(model.T, model.Firms, bounds=(0, None))
        model.capital_allocation = Var(model.T, model.Firms, bounds=(0, None))
        model.wages = Var(model.T, model.Firms, bounds=(self.config.MINIMUM_WAGE, None))
        model.relative_price = Var(model.T, bounds=(0.1, 10))

        # Define objective function
        def total_welfare(model):
            return sum(
                sum(
                    log(max(
                        sum(model.wages[t, i] * model.labor_allocation[t, i] for i in model.Firms),
                        1e-6
                    )) / (1 + model.discount_rate) ** (t - 1)
                    for t in model.T
                )
            )

        model.welfare = Objective(rule=total_welfare, sense=maximize)

        # Define constraints
        def labor_market_clearing(model, t):
            return sum(model.labor_allocation[t, i] for i in model.Firms) == model.num_workers

        model.labor_market_constraint = Constraint(model.T, rule=labor_market_clearing)

        def capital_market_clearing(model, t):
            capital_production = sum(
                self.calculate_firm1_production(
                    [model.labor_allocation[t, i] for i in range(1, len(self.firm1s) + 1)],
                    [model.capital_allocation[t, i] for i in range(1, len(self.firm1s) + 1)]
                )
            )
            capital_demand = sum(model.capital_allocation[t, i] for i in range(len(self.firm1s) + 1, self.num_firms + 1))
            return capital_production == capital_demand

        model.capital_market_constraint = Constraint(model.T, rule=capital_market_clearing)

        def consumption_market_clearing(model, t):
            total_production = sum(
                self.calculate_firm2_production(
                    [model.labor_allocation[t, i] for i in range(len(self.firm1s) + 1, self.num_firms + 1)],
                    [model.capital_allocation[t, i] for i in range(len(self.firm1s) + 1, self.num_firms + 1)]
                )
            )
            worker_income = sum(model.wages[t, i] * model.labor_allocation[t, i] for i in model.Firms)
            return total_production == worker_income

        model.consumption_market_constraint = Constraint(model.T, rule=consumption_market_clearing)

        def firm1_budget_constraint(model, t, i):
            labor_cost = model.wages[t, i] * model.labor_allocation[t, i]
            revenue = model.relative_price[t] * self.calculate_firm1_production(
                [model.labor_allocation[t, i]], [model.capital_allocation[t, i]]
            )[0]
            return revenue >= labor_cost

        model.firm1_budget_constraint = Constraint(model.T, RangeSet(1, len(self.firm1s)),
                                                   rule=firm1_budget_constraint)

        def firm2_budget_constraint(model, t, i):
            actual_i = i + len(self.firm1s)
            labor_cost = model.wages[t, actual_i] * model.labor_allocation[t, actual_i]
            capital_cost = model.relative_price[t] * model.capital_allocation[t, actual_i]
            revenue = self.calculate_firm2_production(
                [model.labor_allocation[t, actual_i]],
                [model.capital_allocation[t, actual_i]]
            )[0]
            return revenue >= labor_cost + capital_cost

        model.firm2_budget_constraint = Constraint(model.T, RangeSet(1, len(self.firm2s)),
                                                   rule=firm2_budget_constraint)

        # Solve the model
        solver = SolverFactory('ipopt')
        solver.options['max_iter'] = 3000
        solver.options['tol'] = 1e-6
        results = solver.solve(model, tee=True)

        # Check solver status
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            print("Optimal solution found.")
        else:
            print("Solver did not find an optimal solution. Status:", results.solver.status)

        # Extract and process results
        labor_allocation = np.array([[value(model.labor_allocation[t, i]) for i in model.Firms] for t in model.T])
        capital_allocation = np.array([[value(model.capital_allocation[t, i]) for i in model.Firms] for t in model.T])
        wages = np.array([[value(model.wages[t, i]) for i in model.Firms] for t in model.T])
        relative_price = np.array([value(model.relative_price[t]) for t in model.T])

        return {
            'labor_allocation': labor_allocation,
            'capital_allocation': capital_allocation,
            'wages': wages,
            'relative_price': relative_price
        }

    def calculate_firm1_production(self, labor, capital):
        return [firm.productivity * (l ** (1 - self.config.CAPITAL_ELASTICITY)) * (k ** self.config.CAPITAL_ELASTICITY)
                for firm, l, k in zip(self.firm1s, labor, capital)]

    def calculate_firm2_production(self, labor, capital):
        return [firm.productivity * (l ** (1 - self.config.CAPITAL_ELASTICITY)) * (k ** self.config.CAPITAL_ELASTICITY)
                for firm, l, k in zip(self.firm2s, labor, capital)]

    def apply_decisions(self, decisions):
        labor_allocation = decisions['labor_allocation'][0]
        capital_allocation = decisions['capital_allocation'][0]
        wages = decisions['wages'][0]
        relative_price = decisions['relative_price'][0]

        for i, firm in enumerate(self.firms):
            firm.apply_central_decision(labor_allocation[i], capital_allocation[i], wages[i])
            if isinstance(firm, Firm1):
                firm.price = relative_price
            else:
                firm.price = 1

        total_labor = int(np.sum(labor_allocation))
        employed_workers = np.random.choice(self.workers, size=total_labor, replace=False)
        for worker in self.workers:
            if worker in employed_workers:
                worker.apply_central_decision(True, np.mean(wages), worker.consumption)
            else:
                worker.apply_central_decision(False, 0, worker.consumption)

        self.model.relative_price = relative_price

    def update_model(self, optimal_solution):
        labor_allocation = optimal_solution['labor_allocation'][0]
        capital_allocation = optimal_solution['capital_allocation'][0]
        wages = optimal_solution['wages'][0]
        relative_price = optimal_solution['relative_price'][0]

        for i, firm in enumerate(self.firms):
            firm.labor_demand = labor_allocation[i]
            firm.capital = capital_allocation[i]
            firm.wage = wages[i]
            if isinstance(firm, Firm1):
                firm.price = relative_price
            else:
                firm.price = 1

            if isinstance(firm, Firm1):
                firm.production = self.calculate_firm1_production([labor_allocation[i]], [capital_allocation[i]])[0]
            else:
                firm.production = self.calculate_firm2_production([labor_allocation[i]], [capital_allocation[i]])[0]

            firm.inventory += firm.production

        total_labor = np.sum(labor_allocation)
        for worker in self.workers:
            if total_labor > 0:
                worker.employed = True
                worker.wage = np.mean(wages)
                worker.savings += worker.wage
            else:
                worker.employed = False
                worker.wage = 0

        self.model.global_accounting.update_market_demand(sum(firm.production for firm in self.firm2s))
        self.model.relative_price = relative_price

    def run_simulation(self, steps):
        for step in range(steps):
            print(f"\n--- Step {step + 1} ---")
            optimal_solution = self.optimize()
            self.update_model(optimal_solution)
            self.print_solution(step, optimal_solution)

    def print_solution(self, step, optimal_solution):
        labor_allocation = optimal_solution['labor_allocation'][0]
        capital_allocation = optimal_solution['capital_allocation'][0]
        wages = optimal_solution['wages'][0]
        relative_price = optimal_solution['relative_price'][0]

        print("Labor Allocation:", labor_allocation)
        print("Capital Allocation:", capital_allocation)
        print("Wages:", wages)
        print(f"Relative Price (Capital/Consumption): {relative_price:.2f}")

        total_production = sum(self.calculate_firm2_production(
            labor_allocation[len(self.firm1s):],
            capital_allocation[len(self.firm1s):]
        ))
        print(f"Total Consumption Good Production: {total_production:.2f}")

        total_capital_production = sum(self.calculate_firm1_production(
            labor_allocation[:len(self.firm1s)],
            capital_allocation[:len(self.firm1s)]
        ))
        print(f"Total Capital Good Production: {total_capital_production:.2f}")

        total_welfare = np.sum(np.log(np.maximum(np.sum(wages * labor_allocation), 1e-6)))
        print(f"Total Welfare: {total_welfare:.2f}")

# Usage
economy_model = EconomyModel(num_workers=100, num_firm1=5, num_firm2=5, mode='centralized')
planner = DynamicCentralPlanner(economy_model)
planner.run_simulation(steps=50)