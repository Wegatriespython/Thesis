import numpy as np
from typing import Dict, List, Callable



def define_model(aggregate=False):
    # Sets
    T = range(10)  # Time periods
    F = ['firm1_1', 'firm1_2', 'firm2_1', 'firm2_2', 'firm2_3']  # All firms
    F1 = ['firm1_1', 'firm1_2']  # Capital goods firms
    F2 = ['firm2_1', 'firm2_2', 'firm2_3']  # Consumption goods firms

    # Parameters
    N = 1000  # Total number of workers
    K_total = 10000  # Total initial capital
    alpha = 0.3  # Capital elasticity
    delta = 0.05  # Discount rate
    rho = 0.1  # Depreciation rate
    w_min = 5  # Minimum wage

    def A(i: str) -> float:
        return {'firm1_1': 1.2, 'firm1_2': 1.3, 'firm2_1': 1.0, 'firm2_2': 1.1, 'firm2_3': 1.2}[i]

    def L(state: Dict, t: int, i: str) -> float:
        return state['L'][t][i]

    def K(state: Dict, t: int, i: str) -> float:
        return state['K'][t][i]

    def w(state: Dict, t: int, i: str) -> float:
        return state['w'][t][i]

    def p(state: Dict, t: int) -> float:
        return state['p'][t]

    def labor_market_clearing(state: Dict, t: int) -> bool:
        return sum(L(state, t, i) for i in F) <= N

    def capital_market_clearing(state: Dict, t: int) -> bool:
        produced = sum(A(i) * L(state, t, i)**(1-alpha) * K(state, t, i)**alpha for i in F1)
        consumed = sum(K(state, t, i) for i in F2)
        return produced >= consumed

    def consumption_market_clearing(state: Dict, t: int) -> bool:
        if t == 0:
            return True
        produced = sum(A(i) * L(state, t, i)**(1-alpha) * K(state, t, i)**alpha for i in F2)
        consumed = sum(w(state, t-1, i) * L(state, t-1, i) for i in F)
        return produced >= consumed

    def firm1_budget_constraint(state: Dict, t: int, i: str) -> bool:
        if t == 0:
            return True
        revenue = p(state, t) * A(i) * L(state, t, i)**(1-alpha) * K(state, t, i)**alpha
        cost = w(state, t, i) * L(state, t, i)
        return revenue >= cost

    def firm2_budget_constraint(state: Dict, t: int, i: str) -> bool:
        if t == 0:
            return True
        revenue = A(i) * L(state, t-1, i)**(1-alpha) * K(state, t-1, i)**alpha
        cost = w(state, t, i) * L(state, t, i) + p(state, t) * K(state, t, i)
        return revenue >= cost

    def capital_conservation_firm1(state: Dict, t: int, i: str) -> bool:
        if t == 0:
            return True
        return K(state, t, i) == K(state, 0, i) * (1 - rho)**t

    def capital_conservation_firm2(state: Dict, t: int) -> bool:
        if t == 0:
            return True
        produced = sum(A(i) * L(state, t-1, i)**(1-alpha) * K(state, t-1, i)**alpha for i in F1)
        existing = sum(K(state, t-1, i) * (1-rho) for i in F2)
        used = sum(K(state, t, i) for i in F2)
        return produced + existing == used

    def minimum_wage_constraint(state: Dict, t: int, i: str) -> bool:
        return w(state, t, i) >= w_min

    def minimum_consumption(state: Dict, t: int) -> bool:
        consumption = sum(A(i) * L(state, t, i)**(1-alpha) * K(state, t, i)**alpha for i in F2)
        return consumption >= N

    def objective_function(state: Dict) -> float:
        total_welfare = 0
        for t in T:
            period_welfare = np.log(max(sum(w(state, t, i) * L(state, t, i) for i in F), 1e-6))
            total_welfare += period_welfare / (1 + delta)**t
        return total_welfare
    def agg_labor_market_clearing(state: Dict, t: int) -> bool:
        return state['L']['firm1'] + state['L']['firm2'] <= N

    def agg_capital_market_clearing(state: Dict, t: int) -> bool:
        produced = A('firm1') * state['L']['firm1']**(1-alpha) * state['K']['firm1']**alpha
        consumed = state['K']['firm2']
        return produced >= consumed

    def agg_consumption_market_clearing(state: Dict, t: int) -> bool:
        if t == 0:
            return True
        produced = A('firm2') * state['L']['firm2']**(1-alpha) * state['K']['firm2']**alpha
        consumed = state['w']['firm1'] * state['L']['firm1'] + state['w']['firm2'] * state['L']['firm2']
        return produced >= consumed

    def agg_firm1_budget_constraint(state: Dict, t: int) -> bool:
        if t == 0:
            return True
        revenue = state['p'] * A('firm1') * state['L']['firm1']**(1-alpha) * state['K']['firm1']**alpha
        cost = state['w']['firm1'] * state['L']['firm1']
        return revenue >= cost

    def agg_firm2_budget_constraint(state: Dict, t: int) -> bool:
        if t == 0:
            return True
        revenue = A('firm2') * state['L']['firm2']**(1-alpha) * state['K']['firm2']**alpha
        cost = state['w']['firm2'] * state['L']['firm2'] + state['p'] * state['K']['firm2']
        return revenue >= cost

    def agg_minimum_wage_constraint(state: Dict, t: int) -> bool:
        return state['w']['firm1'] >= w_min and state['w']['firm2'] >= w_min

    def agg_minimum_consumption(state: Dict, t: int) -> bool:
        consumption = A('firm2') * state['L']['firm2']**(1-alpha) * state['K']['firm2']**alpha
        return consumption >= N

    # New aggregated objective function
    def agg_objective_function(state: Dict) -> float:
        total_wage = state['w']['firm1'] * state['L']['firm1'] + state['w']['firm2'] * state['L']['firm2']
        return np.log(max(total_wage, 1e-6)) / (1 + delta)**state['t']
    def generate_initial_state() -> Dict:
        state = {'t': 0, 'L': {}, 'K': {}, 'w': {}, 'p': {}}
        for t in T:
            if aggregate:
                state['L'][t] = {'firm1': N / 2, 'firm2': N / 2}
                state['K'][t] = {'firm1': K_total / 2, 'firm2': K_total / 2}
                state['w'][t] = {'firm1': w_min, 'firm2': w_min}
            else:
                state['L'][t] = {i: N / len(F) for i in F}
                state['K'][t] = {i: K_total / len(F) for i in F}
                state['w'][t] = {i: w_min for i in F}
            state['p'][t] = 1.0
        return state

    def transition_state(state: Dict) -> Dict:
        new_state = {}
        for key in state:
            if isinstance(state[key], dict):
                new_state[key] = {k: v.copy() if isinstance(v, dict) else v for k, v in state[key].items()}
            else:
                new_state[key] = state[key]

        t = state['t']
        next_t = t + 1
        new_state['t'] = next_t

        # Initialize next time step for K, L, w, and p if they don't exist
        for var in ['K', 'L', 'w', 'p']:
            if next_t not in new_state[var]:
                new_state[var][next_t] = new_state[var][t].copy() if isinstance(new_state[var][t], dict) else new_state[var][t]

        # Apply depreciation to capital
        for i in F:
            new_state['K'][next_t][i] = new_state['K'][t][i] * (1 - rho)

        # Transfer capital from F1 to F2
        produced_capital = sum(A(i) * L(new_state, t, i)**(1-alpha) * K(new_state, t, i)**alpha for i in F1)
        for i in F2:
            new_state['K'][next_t][i] += produced_capital / len(F2)

        return new_state

        model = {
            'sets': {'T': T, 'F': F, 'F1': F1, 'F2': F2},
            'parameters': {'A': A, 'N': N, 'K_total': K_total, 'alpha': alpha,
                           'delta': delta, 'rho': rho, 'w_min': w_min},
            'variables': {'L': L, 'K': K, 'w': w, 'p': p},
            'constraints': [
                labor_market_clearing,
                capital_market_clearing,
                consumption_market_clearing,
                firm1_budget_constraint,
                firm2_budget_constraint,
                capital_conservation_firm1,
                capital_conservation_firm2,
                minimum_wage_constraint,
                minimum_consumption
            ],
            'objective': objective_function,
            'initial_state': generate_initial_state,
            'transition': transition_state
        }
        if aggregate:
            model['constraints'] = [
                agg_labor_market_clearing,
                agg_capital_market_clearing,
                agg_consumption_market_clearing,
                agg_firm1_budget_constraint,
                agg_firm2_budget_constraint,
                agg_minimum_wage_constraint,
                agg_minimum_consumption
            ]
            model['objective'] = agg_objective_function

        return model
