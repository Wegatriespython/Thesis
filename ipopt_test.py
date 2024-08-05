
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Create a simple model
model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(0,10))
model.y = pyo.Var(bounds=(0,10))
model.obj = pyo.Objective(expr = model.x**2 + model.y**2)
model.con = pyo.Constraint(expr = model.x + model.y >= 5)

# Solve the model
opt = SolverFactory('ipopt')
opt.options['linear_solver'] = 'ma97'  # Specify HSL solver
results = opt.solve(model, tee=True)

# Display results
model.display()
