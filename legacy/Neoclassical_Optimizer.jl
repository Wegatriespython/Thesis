using Optim
using ForwardDiff  # For automatic differentiation
using Plots

# Cobb-Douglas production function
function cobb_douglas(productivity, capital, labor, capital_elasticity)
  return productivity * capital^capital_elasticity * labor^(1 - capital_elasticity)
end

# Profit function (negative for minimization)
function profit(labor_capital, budget, current_capital, current_price, current_productivity, 
                expected_demand, avg_wage, avg_capital_price, capital_elasticity)
  labor, capital = labor_capital
  production = min(cobb_douglas(current_productivity, capital, labor, capital_elasticity), expected_demand)
  total_cost = labor * avg_wage + (capital - current_capital) * avg_capital_price
  return -(production * current_price - total_cost)
end

# Parameters (example values)
budget = 1000.0
current_capital = 50.0
current_labor = 10.0
current_price = 10.0
current_productivity = 1.0
expected_demand = 100.0
avg_wage = 5.0
avg_capital_price = 20.0
capital_elasticity = 0.3

# Initial guess
initial_guess = [current_labor, current_capital]

# Bounds (labor >= 0, capital >= 1)
lower_bounds = [0.0, 1.0]
upper_bounds = [Inf, Inf]

# Optimization using Optim.jl (e.g., L-BFGS-B algorithm)
result = optimize(
  x -> profit(x, budget, current_capital, current_price, current_productivity, 
              expected_demand, avg_wage, avg_capital_price, capital_elasticity),
  lower_bounds,
  upper_bounds,
  initial_guess,
  Fminbox(LBFGS())
)

# Optimal labor and capital
optimal_labor, optimal_capital = Optim.minimizer(result)

# Calculate optimal production
optimal_production = cobb_douglas(current_productivity, optimal_capital, optimal_labor, capital_elasticity)

println("Optimal Labor: ", optimal_labor)
println("Optimal Capital: ", optimal_capital)
println("Optimal Production: ", optimal_production)

# --- Calculate PPF ---
labor_range = range(0, stop=20, length=100) 
ppf = zeros(length(labor_range))

for (i, labor) in enumerate(labor_range)
    # Find the maximum capital affordable given the budget and labor
    max_affordable_capital = (budget - labor * avg_wage) / avg_capital_price + current_capital
    
    # Calculate production at full capital utilization
    ppf[i] = cobb_douglas(current_productivity, max_affordable_capital, labor, capital_elasticity)
end

plt = plot(labor_range, ppf, label="Production Possibility Frontier", linewidth=2)
scatter!([optimal_labor], [optimal_production], color="red", markersize=8, label="Optimal Production")

xlabel!("Labor")
ylabel!("Production")
title!("Production Possibility Frontier and Optimal Solution")
grid(true, true)

savefig(plt, "ppf_plot.png")
