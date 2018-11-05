import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import math
import sys

sys.setrecursionlimit(11000)

def mutate(encoding):
    idx = int(round(random.uniform(0, len(encoding)-1)))
    new_encoding = encoding.copy()
    new_encoding[idx] = int(round(random.uniform(0, 1)))
    return new_encoding;

def crossover(e_1, e_2):
    new_encoding = e_2.copy()
    size = int(len(e_1)/2)
    for i in range( size):
        new_encoding[i] = e_1[i]
    return new_encoding

def do_generation(graph, population, path_options, depth = 0):
    cost = get_cost(graph, population[9]["encoding"], path_options)
    print(cost)
    if cost <= 0 or depth > 10000:
        print('DONE')
        return population[0]["encoding"]
    else:
        new_population = population.copy()
        for c in range(4):
            encoding = mutate(population[c]["encoding"])
            new_encoding = {
                "encoding": encoding,
                "cost": get_cost(graph, encoding, path_options)
            }
            new_population[c] = new_encoding

        encoding = crossover(population[8]["encoding"], population[9]["encoding"])
        new_encoding = {
                "encoding": encoding,
                "cost": get_cost(graph, encoding, path_options)
            }
        new_population[7] = new_encoding

        encoding = crossover(population[9]["encoding"], population[8]["encoding"])
        new_encoding = {
                "encoding": encoding,
                "cost": get_cost(graph, encoding, path_options)
            }
        new_population[6] = new_encoding

        new_population = sorted(new_population, key=lambda x: x["cost"], reverse=True)
        # print('new generation')
        # for p in new_population:
        #     print(p["cost"])

        # print('##')
        do_generation(graph, new_population, path_options, depth +1)
    pass


def get_decision_index(arr):
    return int(2 * arr[0] + arr[1])


def get_cost(graph, encoding, path_options):
    nodes = graph.nodes()
    edges = {}

    idx = 0
    for s in nodes:
        for d in nodes:
            if d > s:
                current_path_encoding = encoding[idx: idx+2]
                current_path_decision = get_decision_index(current_path_encoding)
                key = 'path_' + str(s) + '-' + str(d)
                current_path_options = path_options[key]
                if current_path_decision > len(current_path_options)-1:
                    # print('inf')
                    current_path_decision = current_path_decision -1
                    return math.inf

                current_path = current_path_options[current_path_decision]
                
                for i in range(len(current_path)-1):
                    link_start = current_path[i]
                    link_end = current_path[i+1]
                    normalized_indizes = np.sort([link_start, link_end])
                    key = 'edge_' + str(normalized_indizes[0]) + '-' + str(normalized_indizes[1])
                    if key in edges:
                        edges[key] = edges[key] +1
                    else:
                        edges[key] = 1
                    
                idx = idx + 1
    
    cost = 0
    for key in edges:
        demand = edges[key]
        c_1 = math.floor(demand / 4)
        c_2 = demand - 4 * c_1
        cost += c_1 * 2.5 + c_2
    # print(cost)
    return cost


def run_genetic_algorithm():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(0, 3)
    G.add_edge(1, 4)
    G.add_edge(2, 5)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    # nx.draw(G, with_labels = True)
    # plt.show()
    nodes = G.nodes()

    path_options = {}

    for s in nodes:
        for d in nodes:
            if d > s:
                # print('\n####  ',s,d, '  ####')
                name = 'path_' + str(s) + '-' + str(d)
                path_options[name] = list(nx.all_simple_paths(G, source=s, target=d))

    print('Number of pathes ', len(path_options))

    population = []

    # initialize with random decision
    for pop in range(10):
        # 2 bit as decision for every encoding
        encoding = np.zeros(2 * len(path_options))
        for i in range(len(encoding)):
            encoding[i] = int(round(random.uniform(0, 1)))

        population.append({
            "cost": i,#get_cost(G, encoding, path_options),
            "encoding": encoding
        })
        population = sorted(population, key=lambda x: x["cost"], reverse=True)
    for p in population:
        print(p["cost"])

    do_generation(G, population, path_options)
    pass


run_genetic_algorithm()
