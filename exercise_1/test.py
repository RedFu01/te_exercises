from gurobipy import *
try:
    # Create a new model.
    m = Model("same old problem")
    # Create variables.
    x_A = m.addVar(vtype=GRB.INTEGER, name="x_A")
    x_B = m.addVar(vtype=GRB.INTEGER, name="x_B")
    # Set objective.
    m.setObjective(25*x_A + 30*x_B, GRB.MAXIMIZE)
    # Add time constraint.
    m.addConstr((1/200)*x_A + (1/140)*x_B <= 40, "Time")
    # Add product A limit.
    m.addConstr(0 <= x_A <= 6000, "A_Limit")
    # Add product B limit.
    m.addConstr(0 <= x_B <= 4000, "B_Limit")
    m.optimize()
    for v in m.getVars():
            print(v.varName, v.x)
    print("Obj:", m.objVal)
except GurobiError:
    print("Error reported")