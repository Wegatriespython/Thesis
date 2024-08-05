import numpy as np
from Simple_profit_maxxing import profit_maximization

def comprehensive_sensitivity_analysis():
    # Base case parameters
    base_params = {
        "current_capital": 20,
        "current_labor": 0,
        "current_price": 1,
        "current_productivity": 1,
        "expected_demand": [30] * 25,
        "expected_price": [1] * 25,
        "capital_price": 1,
        "capital_elasticity": 0.3,
        "current_inventory": 3.6,
        "depreciation_rate": 0.1,
        "expected_periods": 25,
        "discount_rate": 0.05,
        "budget": 19.6,
        "wage": 1
    }

    # Parameters to analyze and their ranges
    sensitivity_params = {
        "expected_price": np.linspace(0.1, 2, 20),
        "capital_price": np.linspace(0.1, 2, 20),
        "expected_demand": np.linspace(10, 50, 20),
        "expected_periods": range(5, 50, 5),
        "discount_rate": np.linspace(0.01, 0.1, 10)
    }

    results = {}

    for param, values in sensitivity_params.items():
        print(f"\nSensitivity analysis for {param}:")
        param_results = []
        for value in values:
            test_params = base_params.copy()
            if param == "expected_periods":
                test_params[param] = value
                test_params["expected_demand"] = base_params["expected_demand"][:value]
                test_params["expected_price"] = base_params["expected_price"][:value]
            elif param in ["expected_price", "expected_demand"]:
                test_params[param] = [value] * base_params["expected_periods"]
            else:
                test_params[param] = value

            try:
                result = profit_maximization(**test_params)
                if result is not None:
                    param_results.append((value, result['optimal_labor'], result['optimal_capital'], result['optimal_production']))
                else:
                    print(f"Optimization failed for {param} = {value}")
            except Exception as e:
                print(f"Error occurred for {param} = {value}: {str(e)}")

        results[param] = param_results

        if param_results:
            print(f"{'Value':<10} {'Labor':<10} {'Capital':<10} {'Production':<10}")
            for value, labor, capital, production in param_results:
                print(f"{value:<10.2f} {labor:<10.2f} {capital:<10.2f} {production:<10.2f}")
        else:
            print("No valid results for this parameter.")

    return results

def test_linear_solvers():
    base_params = {
        "current_capital": 20,
        "current_labor": 0,
        "current_price": 1,
        "current_productivity": 1,
        "expected_demand": [30] * 25,
        "expected_price": [1] * 25,
        "capital_price": 1,
        "capital_elasticity": 0.3,
        "current_inventory": 3.6,
        "depreciation_rate": 0.1,
        "expected_periods": 25,
        "discount_rate": 0.05,
        "budget": 19.6,
        "wage": 1
    }

    linear_solvers = ['mumps', 'ma27', 'ma57', 'ma97']

    for solver_option in linear_solvers:
        print(f"\nTesting with linear solver: {solver_option}")
        try:
            result = profit_maximization(**base_params, linear_solver=solver_option)
            if result is not None:
                print("Optimization successful:")
                for key, value in result.items():
                    print(f"{key}: {value}")
            else:
                print("Optimization failed to find a solution")
        except Exception as e:
            print(f"Error occurred: {str(e)}")

def numerical_stability_test():
    base_params = {
        "current_capital": 20,
        "current_labor": 0,
        "current_price": 1,
        "current_productivity": 1,
        "expected_demand": [30] * 25,
        "expected_price": [1] * 25,
        "capital_price": 1,
        "capital_elasticity": 0.3,
        "current_inventory": 3.6,
        "depreciation_rate": 0.1,
        "expected_periods": 25,
        "discount_rate": 0.05,
        "budget": 19.6,
        "wage": 1
    }

    scale_factors = [1, 2, 10, 47, 300]

    for factor in scale_factors:
        print(f"\nTesting with scale factor: {factor}")
        test_params = base_params.copy()
        for key in ["current_capital", "current_price", "expected_demand", "expected_price", "capital_price", "current_inventory", "budget", "wage"]:
            if isinstance(test_params[key], list):
                test_params[key] = [x * factor for x in test_params[key]]
            else:
                test_params[key] *= factor

        try:
            result = profit_maximization(**test_params)
            if result is not None:
                print("Optimization successful:")
                for key, value in result.items():
                    print(f"{key}: {value}")
            else:
                print("Optimization failed to find a solution")
        except Exception as e:
            print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    results = comprehensive_sensitivity_analysis()
    test_linear_solvers()
    numerical_stability_test()

    # Additional analysis of results
    print("\nAnalysis of sensitivity results:")
    for param, param_results in results.items():
        if param_results:
            values, labors, capitals, productions = zip(*param_results)
            print(f"\n{param}:")
            print(f"Range of optimal labor: {min(labors):.2f} to {max(labors):.2f}")
            print(f"Range of optimal capital: {min(capitals):.2f} to {max(capitals):.2f}")
            print(f"Range of optimal production: {min(productions):.2f} to {max(productions):.2f}")
        else:
            print(f"\n{param}: No valid results")
