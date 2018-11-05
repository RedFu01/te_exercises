from gurobipy import *

def uncapacitated_problem():
    # Create a new model.
    m = Model("Uncapacitated Problem")
    # Create variables.

    variables = {}
    objective = 0
    costs = [1, 2.5, 4]
    capacities = [1, 4, 8]
    trafficDemand = 1

    nodes = 17
    cableTypes = 3

    linksTable = [
    #    0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
        [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    ]


    for i in range(nodes):
        for j in range(nodes):
            for s in range(nodes):
                for d in range(nodes):
                    if linksTable[i][j]:
                        name= "x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)
                        variable = m.addVar(vtype=GRB.BINARY, name=name)
                        variables[name] = variable

    for n in range(cableTypes):
        for i in range(nodes):
            for j in range(nodes):
                if linksTable[i][j]:
                    name = "l_" + str(i) + "," + str(j) + "," + str(n)
                    variable = m.addVar(vtype=GRB.INTEGER, name=name)
                    variables[name] = variable
                    m.addConstr(0 <= variable, name)

                    objective = objective + costs[n] * variable

    
    # Objective function
    m.setObjective(objective, GRB.MINIMIZE)

    # Constraints

    for s in range(nodes):
        for d in range(nodes):
            for i in range(nodes):
                constraint = 0
                for j in range(nodes):
                    if linksTable[i][j]:
                        x1 = variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)]
                        x2 = variables["x_" + str(j) + "," + str(i) + "_" + str(s) + "," + str(d)]
                        constraint = constraint + x1 - x2

                result = 0
                if s == i:
                    result = 1
                elif d == i:
                    result = -1

                if s != d:
                    m.addConstr(constraint == result, "flow_" + str(s) + str(d) + str(i))
    
    for i in range(nodes):
        for j in range(nodes):
            if linksTable[i][j]:
                expression = 0
                for s in range(nodes):
                    for d in range(nodes):
                        expression = expression + variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)]

                result = 0
                for n in range(cableTypes):
                    result = result + capacities[n] * variables["l_" + str(i) + "," + str(j) + "," + str(n)]
                
                m.addConstr(expression <= result, "capacity_" + str(i) + str(j))


    m.optimize()

    for v in m.getVars():
        if v.x > 0:
            print(v.varName, v.x)
    print("Obj:", m.objVal)


def capacitated_problem():
    # Create a new model.
    m = Model("Capacitated Problem")
    # Create variables.

    variables = {}
    objective = 0
    capacity = 4
    trafficDemand = 1

    nodes = 17

    linksTable = [
        [0, 1, 0, 1, 0, 0],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 0]
    ]


    for i in range(nodes):
        for j in range(nodes):
            for s in range(nodes):
                for d in range(nodes):
                    if linksTable[i][j]:
                        name= "x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)
                        variable = m.addVar(vtype=GRB.BINARY, name=name)
                        variables[name] = variable

    u = m.addVar(vtype=GRB.BINARY, name="U")
    m.addConstr(0 <= u <= 1, name)
    

    
    # Objective function
    m.setObjective(u, GRB.MINIMIZE)

    # Constraints

    for s in range(nodes):
        for d in range(nodes):
            for i in range(nodes):
                constraint = 0
                for j in range(nodes):
                    if linksTable[i][j]:
                        x1 = variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)]
                        x2 = variables["x_" + str(j) + "," + str(i) + "_" + str(s) + "," + str(d)]
                        constraint = constraint + x1 - x2

                result = 0
                if s == i:
                    result = 1
                elif d == i:
                    result = -1

                print(s,d,i,result)

                if s != d:
                    m.addConstr(constraint == result, "flow_" + str(s) + str(d) + str(i))
    
    for i in range(nodes):
        for j in range(nodes):
            if linksTable[i][j]:
                expression = 0
                for s in range(nodes):
                    for d in range(nodes):
                        expression = expression + variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)]
                
                m.addConstr(expression/ capacity <= u, "utilization_" + str(i) + str(j))


    m.optimize()

    for v in m.getVars():
            print(v.varName, v.x)
    print("Obj:", m.objVal)

try:
   uncapacitated_problem()   
except GurobiError:
    print("Error reported")