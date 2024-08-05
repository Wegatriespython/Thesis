import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import numpy as np

def profit_maximization(
        current_capital, current_labor, current_price, current_productivity,
        expected_demand, expected_price, capital_price, capital_elasticity,
        current_inventory, depreciation_rate, expected_periods, discount_rate,
        budget, wage, linear_solver='mumps'):

    model = pyo.ConcreteModel()

    # Sets
    model.T = pyo.RangeSet(0, expected_periods - 1)

    # Scaling factors
    scale_capital = max(1, current_capital)
    scale_labor = max(1, current_labor)
    scale_price = max(1, current_price)
    scale_demand = max(1, max(expected_demand))

    # Variables with scaling and safeguarded log transformation
    model.labor = pyo.Var(domain=pyo.NonNegativeReals, initialize=max(1e-6, current_labor))
    model.capital = pyo.Var(domain=pyo.NonNegativeReals, initialize=max(1e-6, current_capital))
    model.production = pyo.Var(domain=pyo.NonNegativeReals, initialize=1e-6)
    model.inventory = pyo.Var(model.T, domain=pyo.NonNegativeReals, initialize=max(1e-6, current_inventory))
    model.sales = pyo.Var(model.T, domain=pyo.NonNegativeReals, initialize=1e-6)

    # Objective
    def objective_rule(model):
        return sum(
            (expected_price[t] * model.sales[t] / scale_price
             - wage * model.labor / scale_labor
             - (model.capital - current_capital) * capital_price / scale_capital * (1 if t == 0 else 0)
             - depreciation_rate * expected_price[t] * model.inventory[t] / scale_price
            ) / ((1 + discount_rate) ** t)
            for t in model.T
        )
    model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

    # Constraints
    def production_constraint_rule(model):
        return model.production == current_productivity * (model.capital ** capital_elasticity) * (model.labor ** (1 - capital_elasticity))
    model.production_constraint = pyo.Constraint(rule=production_constraint_rule)

    def budget_constraint_rule(model):
        return (wage * model.labor / scale_labor +
                (model.capital - current_capital) * capital_price / scale_capital <= budget)
    model.budget_constraint = pyo.Constraint(rule=budget_constraint_rule)

    def inventory_balance_rule(model, t):
        if t == 0:
            return model.inventory[t] == current_inventory + model.production - model.sales[t]
        else:
            return model.inventory[t] == model.inventory[t-1] + model.production - model.sales[t]
    model.inventory_balance = pyo.Constraint(model.T, rule=inventory_balance_rule)

    def sales_constraint_demand_rule(model, t):
        return model.sales[t] <= expected_demand[t]
    model.sales_constraint_demand = pyo.Constraint(model.T, rule=sales_constraint_demand_rule)

    def sales_constraint_inventory_rule(model, t):
        return model.sales[t] <= model.inventory[t] + model.production
    model.sales_constraint_inventory = pyo.Constraint(model.T, rule=sales_constraint_inventory_rule)

    # Solve the model
    solver = SolverFactory('ipopt')
    solver.options['max_iter'] = 10000
    solver.options['tol'] = 1e-6
    solver.options['linear_solver'] = linear_solver
    results = solver.solve(model, tee=False)

    # Check if the solver found an optimal solution
    if (results.solver.status == pyo.SolverStatus.ok and
        results.solver.termination_condition == pyo.TerminationCondition.optimal):
        return {
            'optimal_labor': pyo.value(model.labor),
            'optimal_capital': pyo.value(model.capital),
            'optimal_production': pyo.value(model.production),
            'optimal_price': expected_price[0],
            'optimal_sales': [pyo.value(model.sales[t]) for t in model.T],
            'optimal_inventory': [pyo.value(model.inventory[t]) for t in model.T]
        }
    else:
        print(f"Solver status: {results.solver.status}")
        print(f"Termination condition: {results.solver.termination_condition}")
        return None
