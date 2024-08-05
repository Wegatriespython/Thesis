import numpy as np
from scipy.optimize import fsolve

class SimpleCGEModel:
    def __init__(self, A=1.0, alpha=0.3, L_total=100, K_total=1000):
        self.A = A  # Total factor productivity
        self.alpha = alpha  # Capital share
        self.L_total = L_total  # Total labor supply
        self.K_total = K_total  # Total capital supply

    def production_function(self, K, L):
        return self.A * (K ** self.alpha) * (L ** (1 - self.alpha))

    def firm_profit(self, p, w, r, K, L):
        return p * self.production_function(K, L) - w * L - r * K

    def equations(self, vars):
        p1, p2, w, r, L1, K1 = vars
        L2 = self.L_total - L1
        K2 = self.K_total - K1

        # Production
        Y1 = self.production_function(K1, L1)
        Y2 = self.production_function(K2, L2)

        # Profit maximization conditions
        eq1 = p1 * (1 - self.alpha) * Y1 / L1 - w  # MPL1 = w
        eq2 = p2 * (1 - self.alpha) * Y2 / L2 - w  # MPL2 = w
        eq3 = p1 * self.alpha * Y1 / K1 - r  # MPK1 = r
        eq4 = p2 * self.alpha * Y2 / K2 - r  # MPK2 = r

        # Market clearing conditions
        eq5 = Y1 - (K1 + K2)  # Capital goods market
        eq6 = Y2 - (w * self.L_total + r * self.K_total) / p2  # Consumption goods market

        return [eq1, eq2, eq3, eq4, eq5, eq6]

    def solve(self):
        initial_guess = [1, 1, 1, 0.1, self.L_total / 2, self.K_total / 2]
        solution = fsolve(self.equations, initial_guess)
        return solution

    def print_results(self, solution):
        p1, p2, w, r, L1, K1 = solution
        L2 = self.L_total - L1
        K2 = self.K_total - K1

        Y1 = self.production_function(K1, L1)
        Y2 = self.production_function(K2, L2)

        print("Equilibrium Results:")
        print(f"Price of good 1 (capital good): {p1:.4f}")
        print(f"Price of good 2 (consumption good): {p2:.4f}")
        print(f"Wage rate: {w:.4f}")
        print(f"Rental rate of capital: {r:.4f}")
        print(f"Labor in sector 1: {L1:.4f}")
        print(f"Labor in sector 2: {L2:.4f}")
        print(f"Capital in sector 1: {K1:.4f}")
        print(f"Capital in sector 2: {K2:.4f}")
        print(f"Output of good 1: {Y1:.4f}")
        print(f"Output of good 2: {Y2:.4f}")

        # Check market clearing
        print("\nMarket Clearing:")
        print(f"Capital goods: Supply - Demand = {Y1 - (K1 + K2):.4e}")
        print(f"Consumption goods: Supply - Demand = {Y2 - (w * self.L_total + r * self.K_total) / p2:.4e}")

        # Check zero profit condition
        profit1 = self.firm_profit(p1, w, r, K1, L1)
        profit2 = self.firm_profit(p2, w, r, K2, L2)
        print("\nZero Profit Condition:")
        print(f"Profit in sector 1: {profit1:.4e}")
        print(f"Profit in sector 2: {profit2:.4e}")

# Run the model
model = SimpleCGEModel()
solution = model.solve()
model.print_results(solution)