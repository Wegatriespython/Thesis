from Central_Planner.economy_state import EconomyState, Config
from Central_Planner.Central_planner import ImprovedMacroeconomicCentralPlanner
from Central_Planner.firm import production_function
from Central_Planner.worker import calculate_total_wage_income, consumption_function

def check_stock_flow_consistency(prev_state, curr_state, config):
    # Check labor conservation
    labor_consistency = abs(curr_state.labor_firm1 + curr_state.labor_firm2 - curr_state.labor_supply) < 1e-6

    # Check capital conservation
    capital_consistency = abs(curr_state.capital_firm1 + curr_state.capital_firm2 - curr_state.capital_supply) < 1e-6

    # Check financial asset conservation
    total_assets_prev = prev_state.assets_firm1 + prev_state.assets_firm2 + prev_state.worker_savings
    total_assets_curr = curr_state.assets_firm1 + curr_state.assets_firm2 + curr_state.worker_savings
    financial_consistency = abs(total_assets_curr - total_assets_prev) < 1e-6

    # Check goods market clearing
    output_firm1 = production_function(curr_state.labor_firm1, curr_state.capital_firm1, config.productivity, config.labor_share)
    output_firm2 = production_function(curr_state.labor_firm2, curr_state.capital_firm2, config.productivity, config.labor_share)
    total_income = curr_state.wage * curr_state.labor_supply
    consumption = consumption_function(total_income, curr_state.price_firm2, config.consumption_propensity)
    investment = curr_state.capital_firm2  # Capital goods bought by Firm 2
    goods_market_clearing = abs(output_firm2 - consumption) < 1e-6 and abs(output_firm1 - investment) < 1e-6

    return {
        "Labor Consistency": labor_consistency,
        "Capital Consistency": capital_consistency,
        "Financial Consistency": financial_consistency,
        "Goods Market Clearing": goods_market_clearing
    }

def print_state(state, step, config, cumulative_savings_change=0):
    print(f"Step {step}:")
    print(f"  Prices: Firm1 (Capital Goods) = {state.price_firm1:.2f}, Firm2 (Consumption Goods) = {state.price_firm2:.2f}")
    print(f"  Wage: {state.wage:.2f}")
    print(f"  Labor: Firm1 = {state.labor_firm1:.2f}, Firm2 = {state.labor_firm2:.2f}")
    print(f"  Capital: Firm1 = {state.capital_firm1:.2f}, Firm2 (Capital Goods) = {state.capital_firm2:.2f}")
    print(f"  Assets: Firm1 = {state.assets_firm1:.2f}, Firm2 = {state.assets_firm2:.2f}")
    
    total_wage_income = calculate_total_wage_income(state.wage, state.labor_supply)
    consumption = consumption_function(total_wage_income, state.price_firm2, config.consumption_propensity)
    consumption_expenditure = consumption * state.price_firm2
    savings_change = total_wage_income - consumption_expenditure
    
    print(f"  Worker Income: {total_wage_income:.2f}")
    print(f"  Worker Consumption: {consumption_expenditure:.2f}")
    print(f"  Worker Savings Change: {savings_change:.2f}")
    print(f"  Cumulative Savings Change: {cumulative_savings_change:.2f}")
    print(f"  Worker Savings: {state.worker_savings:.2f}")

def main():
    initial_state = EconomyState(
        labor_supply=100,
        capital_supply=1000,
        price_firm1=10,
        price_firm2=5,
        wage=8,
        labor_firm1=50,
        labor_firm2=50,
        capital_firm1=500,
        capital_firm2=500,
        assets_firm1=5000,
        assets_firm2=5000,
        worker_savings=1000
    )

    config = Config(
        productivity=1,
        labor_share=0.7,
        capital_rental_rate=0.05,
        consumption_propensity=0.8,
        minimum_wage=5,
        investment_weight=0.2
    )

    print("Initial State:")
    print_state(initial_state, -1, config)
    print()

    planner = ImprovedMacroeconomicCentralPlanner(initial_state, config)
    simulation_results = planner.run_simulation(steps=10)

    prev_state = initial_state
    cumulative_savings_change = 0
    for i, state in enumerate(simulation_results):
        total_wage_income = calculate_total_wage_income(state.wage, state.labor_supply)
        consumption = consumption_function(total_wage_income, state.price_firm2, config.consumption_propensity)
        consumption_expenditure = consumption * state.price_firm2
        savings_change = total_wage_income - consumption_expenditure
        cumulative_savings_change += savings_change

        print_state(state, i, config, cumulative_savings_change)
        
        consistency_checks = check_stock_flow_consistency(prev_state, state, config)
        print("  Stock-Flow Consistency Checks:")
        for check, result in consistency_checks.items():
            print(f"    {check}: {'Passed' if result else 'Failed'}")
        print()

        prev_state = state

if __name__ == "__main__":
    main()