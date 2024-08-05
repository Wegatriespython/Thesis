import math
import scipy.optimize as optimize

def solve_equilibrium(params):
    """
    Solve for the analytical equilibrium of the one-sector economy,
    aligning with the MCTS model structure.
    
    Parameters:
    - params: dictionary containing model parameters
    
    Returns:
    - equilibrium: dictionary containing equilibrium values
    """
    N = params['N']  # Total labor force
    K = params['K']  # Total capital stock
    alpha = params['alpha']  # Capital share in production function
    delta = params['delta']  # Depreciation rate
    s = params['savings_rate']  # Savings rate

    def objective(x):
        price, labor = x
        capital = K  # Use the full capital stock

        # Production function (now including price)
        Y = price * (labor ** (1 - alpha)) * (capital ** alpha)

        # Consumption (aligned with MCTS model)
        C = Y - delta * capital

        # Utility
        U = math.log(max(C, 1e-6))

        # We want to maximize utility, so return its negative
        return -U

    def constraints(x):
        price, labor = x
        return N - labor  # Ensure labor doesn't exceed N

    # Initial guess
    x0 = [1.0, N/2]

    # Solve the optimization problem
    res = optimize.minimize(objective, x0, method='SLSQP', constraints={'type': 'ineq', 'fun': constraints},
                            bounds=[(0.1, 100), (0, N)])

    if not res.success:
        raise ValueError("Optimization failed to converge.")

    price, labor = res.x
    capital = K

    # Recalculate key values
    Y = price * (labor ** (1 - alpha)) * (capital ** alpha)
    C = Y - delta * capital
    U = math.log(max(C, 1e-6))

    # Calculate wage and rental rate
    w = price * (1 - alpha) * (capital ** alpha) * (labor ** (-alpha))
    r = price * alpha * (capital ** (alpha - 1)) * (labor ** (1 - alpha))

    return {
        'price': price,
        'labor': labor,
        'capital': capital,
        'output': Y,
        'consumption': C,
        'wage': w,
        'rental_rate': r,
        'utility': U
    }

# Example usage
params = {
    'N': 100,  # Total labor force
    'K': 1000,  # Initial capital stock
    'alpha': 0.3,  # Capital share in production function
    'delta': 0.1,  # Depreciation rate
    'savings_rate': 0.2,  # Fraction of output saved/invested
}

equilibrium = solve_equilibrium(params)
print("Revised Analytical Equilibrium Solution:")
for key, value in equilibrium.items():
    print(f"{key}: {value:.4f}")