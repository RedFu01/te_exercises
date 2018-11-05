from gurobipy import *
import networkx as nx
import sys

def uncapacitated_problem():
    # Create Graph
    G=nx.Graph()
    G.add_nodes_from(range(0,17))
    G.add_edge(0,2)
    G.add_edge(0,7)
    G.add_edge(2,3)
    G.add_edge(2,1)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(3,4)
    G.add_edge(3,7)
    G.add_edge(7,5)
    G.add_edge(5,6)
    G.add_edge(6,8)
    G.add_edge(7,8)
    G.add_edge(3,9)
    G.add_edge(4,9)
    G.add_edge(2,1)
    G.add_edge(8,10)
    G.add_edge(9,10)
    G.add_edge(10,12)
    G.add_edge(10,11)
    G.add_edge(11,13)
    G.add_edge(13,14)
    G.add_edge(14,12)
    G.add_edge(12,16)
    G.add_edge(15,16)
    G.add_edge(14,15)

    nodes = G.nodes()

    # Create Model
    m = Model("Uncapacitated Problem")
    variables = {}
    objective = 0
    costs = [1, 2.5, 4]
    capacities = [1, 4, 8]
    trafficDemand = 1
    cableTypes = 3

    for i in nodes:
        for j in nodes:
            for s in nodes:
                for d in nodes:
                    if G.has_edge(i,j):
                            name= "x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)
                            variable = m.addVar(vtype=GRB.BINARY, name=name)
                            variables[name] = variable

    for n in range(cableTypes):
        for i in nodes:
            for j in nodes:
                if G.has_edge(i,j):
                    name = "l_" + str(i) + "," + str(j) + "," + str(n)
                    variable = m.addVar(vtype=GRB.INTEGER, name=name)
                    variables[name] = variable
                    m.addConstr(0 <= variable, name)
                    objective = objective + costs[n] * variable

    m.setObjective(objective, GRB.MINIMIZE)

    for s in nodes:
        for d in nodes:
            for i in nodes:
                constraint = 0
                for j in nodes:
                    if G.has_edge(i,j):
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

    for i in nodes:
        for j in nodes:
            if G.has_edge(i,j) and i<j:
                expression = 0
                for s in nodes:
                    for d in nodes:
                        expression = expression + variables["x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)] + variables["x_" + str(j) + "," + str(i) + "_" + str(s) + "," + str(d)]
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
    # Create Graph
    G=nx.Graph()
    G.add_nodes_from(range(0,17))
    G.add_edge(0,2)
    G.add_edge(0,7)
    G.add_edge(2,3)
    G.add_edge(2,1)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(3,4)
    G.add_edge(3,7)
    G.add_edge(7,5)
    G.add_edge(5,6)
    G.add_edge(6,8)
    G.add_edge(7,8)
    G.add_edge(3,9)
    G.add_edge(4,9)
    G.add_edge(2,1)
    G.add_edge(8,10)
    G.add_edge(9,10)
    G.add_edge(10,12)
    G.add_edge(10,11)
    G.add_edge(11,13)
    G.add_edge(13,14)
    G.add_edge(14,12)
    G.add_edge(12,16)
    G.add_edge(15,16)
    G.add_edge(14,15)

    nodes = G.nodes()

    # Create Model
    m = Model("Capacitated Problem")
    variables = {}
    objective = 0
    costs = [1, 2.5, 4]
    capacities = [1, 4, 8]
    trafficDemand = 1
    capacity = 40
    cableTypes = 3

    for i in nodes:
        for j in nodes:
            for s in nodes:
                for d in nodes:
                    if G.has_edge(i,j):
                            name= "x_" + str(i) + "," + str(j) + "_" + str(s) + "," + str(d)
                            variable = m.addVar(vtype=GRB.BINARY, name=name)
                            variables[name] = variable

    u = m.addVar(name="U")
    m.addConstr(0 <= u <= 1, "Utilization")

    # Objective function
    m.setObjective(u, GRB.MINIMIZE)

    # Constraints
    for s in nodes:
        for d in nodes:
            for i in nodes:
                constraint = 0
                for j in nodes:
                    if G.has_edge(i,j):
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

    for i in nodes:
        for j in nodes:
            if G.has_edge(i,j):
                expression = 0
                for s in nodes:
                    for d in nodes:
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
