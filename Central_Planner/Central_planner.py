import numpy as np
from scipy.optimize import minimize
from Central_Planner.economy_state import EconomyState, Config
from Central_Planner.firm import production_function, calculate_profit, update_firm_assets
from Central_Planner.worker import calculate_total_wage_income, consumption_function, update_worker_savings


#Dont solve for maximum profit. Solve for 0 profit, and then maximize the social welfare function

class ImprovedMacroeconomicCentralPlanner:
    def __init__(self, initial_state: EconomyState, config: Config):
        self.state = initial_state
        self.config = config

    def objective_function(self, x):
        price_capital_goods, price_consumption_goods, wage, labor_firm1, capital_goods_firm2 = x
        
        labor_firm2 = self.state.labor_supply - labor_firm1
        
        # Market 1: Capital-Goods Market
        output_firm1 = production_function(labor_firm1, self.state.capital_firm1, self.config.productivity, self.config.labor_share)
        demand_capital_goods = capital_goods_firm2
        supply_capital_goods = output_firm1
        
        # Market 2: Consumption-Goods Market
        output_firm2 = production_function(labor_firm2, capital_goods_firm2, self.config.productivity, self.config.labor_share)
        total_wage_income = calculate_total_wage_income(wage, self.state.labor_supply)
        consumption = consumption_function(total_wage_income, price_consumption_goods, self.config.consumption_propensity)
        
        # Market clearing conditions
        capital_goods_market_clearing = abs(supply_capital_goods - demand_capital_goods)
        consumption_goods_market_clearing = abs(output_firm2 - consumption)
        labor_market_clearing = abs(self.state.labor_supply - (labor_firm1 + labor_firm2))
        
        # Budget constraints
        revenue_firm1 = price_capital_goods * output_firm1
        cost_firm1 = wage * labor_firm1 + self.config.capital_rental_rate * self.state.capital_firm1
        profit_firm1 = revenue_firm1 - cost_firm1
        
        revenue_firm2 = price_consumption_goods * output_firm2
        cost_firm2 = wage * labor_firm2 + price_capital_goods * capital_goods_firm2
        profit_firm2 = revenue_firm2 - cost_firm2
        
        budget_constraint_firm1 = max(0, -profit_firm1)
        budget_constraint_firm2 = max(0, -profit_firm2)
        
        # Minimum wage constraint
        min_wage_constraint = max(0, self.config.minimum_wage - wage)
        
        # Minimum consumption constraint
        min_consumption_constraint = max(0, 1 - consumption)
        
        # Combine objectives and constraints
        social_welfare = np.log(consumption) + self.config.investment_weight * np.log(max(0.1, capital_goods_firm2))
        constraint_penalty = 1000 * (capital_goods_market_clearing + consumption_goods_market_clearing + 
                                     labor_market_clearing + budget_constraint_firm1 + budget_constraint_firm2 + 
                                     min_wage_constraint + min_consumption_constraint)
        
        return -social_welfare + constraint_penalty

    def optimize(self):
        initial_guess = [self.state.price_firm1, self.state.price_firm2, self.state.wage, 
                         self.state.labor_firm1, self.state.capital_firm2]
        
        bounds = [(0.1, 1000), (0.1, 1000), (self.config.minimum_wage, 100), 
                  (0, self.state.labor_supply), (0, self.state.capital_supply)]
        
        result = minimize(self.objective_function, initial_guess, method='SLSQP', bounds=bounds)
        
        return result.x

    def update_state(self, optimal_solution):
        price_capital_goods, price_consumption_goods, wage, labor_firm1, capital_goods_firm2 = optimal_solution
        
        labor_firm2 = self.state.labor_supply - labor_firm1
        
        # Update prices and allocations
        self.state.price_firm1 = price_capital_goods
        self.state.price_firm2 = price_consumption_goods
        self.state.wage = wage
        self.state.labor_firm1 = labor_firm1
        self.state.labor_firm2 = labor_firm2
        self.state.capital_firm2 = capital_goods_firm2
        
        # Calculate production
        output_firm1 = production_function(labor_firm1, self.state.capital_firm1, self.config.productivity, self.config.labor_share)
        output_firm2 = production_function(labor_firm2, capital_goods_firm2, self.config.productivity, self.config.labor_share)
        
        # Calculate profits
        revenue_firm1 = price_capital_goods * output_firm1
        cost_firm1 = wage * labor_firm1 + self.config.capital_rental_rate * self.state.capital_firm1
        profit_firm1 = revenue_firm1 - cost_firm1
        
        revenue_firm2 = price_consumption_goods * output_firm2
        cost_firm2 = wage * labor_firm2 + price_capital_goods * capital_goods_firm2
        profit_firm2 = revenue_firm2 - cost_firm2
        
        # Update firm assets
        self.state.assets_firm1 = update_firm_assets(self.state.assets_firm1, profit_firm1)
        self.state.assets_firm2 = update_firm_assets(self.state.assets_firm2, profit_firm2)
        
        # Calculate worker income and consumption
        total_wage_income = calculate_total_wage_income(wage, self.state.labor_supply)
        consumption = consumption_function(total_wage_income, price_consumption_goods, self.config.consumption_propensity)
        consumption_expenditure = consumption * price_consumption_goods
        
        # Update worker savings
        savings_change = total_wage_income - consumption_expenditure
        self.state.worker_savings = update_worker_savings(self.state.worker_savings, savings_change)

    def run_simulation(self, steps):
        results = []
        for _ in range(steps):
            optimal_solution = self.optimize()
            self.update_state(optimal_solution)
            results.append(self.state)
        return results

# Usage remains the same as in your example