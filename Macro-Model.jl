using JuMP 
using Ipopt

# Define Sets and Parameters 
T = 10 # Number of time periods
F = 10  # Number of firms
F1 = 1:4 # Indices of capital goods firms
F2 = 5:10 # Indices of consumption goods firms
N = 100.0 # Total number of workers
δ = 0.05 # Discount rate
α = 0.33 # Capital elasticity
A = [1.2, 1.5, 0.8, 1.0, 1.3, 1.1, 0.9, 1.2, 1.4, 1.0] # Productivity of each firm
w_min = 0.1 # Minimum wage
K_Raw_Init = [20.0, 30.0, 25.0, 35.0] # Initial capital for Firm1 firms
K_Intermediate_Init = [15.0, 25.0, 20.0, 30.0, 22.0, 18.0] # Initial capital for Firm2 firms

# Create Model
model = Model(Ipopt.Optimizer) 
set_optimizer_attribute(model, "max_iter", 3000)
set_optimizer_attribute(model, "tol", 1e-4)
set_optimizer_attribute(model, "print_level", 5)  # Increase for more detailed output

# Variables
@variable(model, L[1:T, 1:F] >= 0, start = N / F) # Labor allocation
@variable(model, K_Raw[1:T, F1] >= 0, start = 10.0) # Raw capital allocation for Firm1
@variable(model, K_Intermediate[1:T, F2] >= 0, start = 10.0) # Intermediate capital for Firm2
@variable(model, w[1:T, 1:F] >= w_min, start = 1.0) # Wage rate
@variable(model, 0.1 <= p[1:T] <= 100, start = 1.0) # Relative price

# Objective function 
@NLobjective(model, Max, 
    sum(1/(1+δ)^(t-1) * log(sum(w[t,i]*L[t,i] for i in 1:F) + 1e-6) 
        for t in 1:T)
)

# Constraints
@constraint(model, [t=1:T], sum(L[t,i] for i in 1:F) == N) # Labor market clearing

@NLconstraint(model, [t=1:T], 
    sum(A[i] * L[t,i]^(1-α) * K_Raw[t,i]^α for i in F1) == 
    sum(K_Intermediate[t,i] for i in F2)) # Capital market clearing

@NLconstraint(model, [t=1:T], 
    sum(A[i] * L[t,i]^(1-α) * K_Intermediate[t,i]^α for i in F2) == 
    sum(w[t,i] * L[t,i] for i in 1:F))  # Consumption market clearing

# Firm budget constraints
@NLconstraint(model, [t=1:T, i in F1], 
    p[t] * A[i] * L[t,i]^(1-α) * K_Raw[t,i]^α == w[t,i] * L[t,i]
)
@NLconstraint(model, [t=1:T, i in F2], 
    A[i] * L[t,i]^(1-α) * K_Intermediate[t,i]^α == 
    w[t,i] * L[t,i] + p[t] * K_Intermediate[t,i] 
)

# Conservation of Firm1 Capital
@constraint(model, [i in F1], sum(K_Raw[t, i] for t in 1:T) == K_Raw_Init[i]) 

# Conservation of Firm2 Capital (with production included)
@NLconstraint(model, [i in F2], 
    sum(A[j] * L[t,j]^(1-α) * K_Raw[t,j]^α for t in 1:T, j in F1) + K_Intermediate_Init[i - 4] == 
    sum(K_Intermediate[t,i] for t in 1:T) 
)

# Solve the model
optimize!(model)

# Check the solution status
if termination_status(model) == MOI.OPTIMAL
    println("Optimal solution found.")
    println("Objective value: ", objective_value(model)) 
    println("Labor allocation (L): ", value.(L))
    # ... access other variables similarly
else
    println("Optimization did not converge to an optimal solution.")
    println("Termination status: ", termination_status(model))
end