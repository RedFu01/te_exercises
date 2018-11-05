from gurobipy import *
import sys

def uncapacitated_problem():
    # Create a new model.
    m = Model("Uncapacitated Problem")
    # Create variables.

    variables = {}
    objective = 0
    costs = [1, 2.5]
    capacities = [1, 4]
    trafficDemand = 1

    nodes = 6

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
                    if linksTable[i][j] and s != d:
                        name= "x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)
                        variable = m.addVar(vtype=GRB.BINARY, name=name)
                        variables[name] = variable

    for n in range(2):
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
                    if linksTable[i][j] and s != d:
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
            if linksTable[i][j] and i<j:
                expression = 0
                for s in range(nodes):
                    for d in range(nodes):
                        if s != d:
                            expression = expression + variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)] + variables["x_" + str(j) + "," + str(i) + "_" + str(s) + "," + str(d)]

                result = 0
                for n in range(2):
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

    nodes = 6

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

    u = m.addVar(name="U")
    m.addConstr(0 <= u <= 1, "U")
    

    
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
                
                m.addConstr(expression / capacity <= u, "utilization_" + str(i) + str(j))


    m.optimize()

    for v in m.getVars():
        if v.x > 0:
            print(v.varName, v.x)
    print("Obj:", m.objVal)

try:
    command = sys.argv[1]
    if command == 'capacitated':
        capacitated_problem() 
    elif command == 'uncapacitated':
        uncapacitated_problem() 
    else:
        print('Invalid args')
      
except GurobiError:
    print("Error reported")