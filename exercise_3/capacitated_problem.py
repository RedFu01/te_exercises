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
    new_value = 0
    if new_encoding[idx] == 0:
        new_value = 1
    new_encoding[idx] = new_value
    return new_encoding

def crossover(e_1, e_2):
    new_encoding = e_2.copy()
    size = int(len(e_1)/2)
    for i in range(size):
        new_encoding[i] = e_1[i]
    return new_encoding

def create_encoding_obj(graph, encoding, path_options):
    return {
        "encoding": encoding,
        "cost": get_cost(graph, encoding, path_options)
    }

def get_random_encoding(length):
    encoding = np.zeros(length)
    for i in range(len(encoding)):
        encoding[i] = int(round(random.uniform(0, 1)))
    return encoding

def get_new_population(graph, old_population, path_options):
    new_population = old_population.copy()
    pop_size = len(old_population)
    encoding_size = len(old_population[0]["encoding"])

    for _ in range(10):
        idx_1 = int(round(random.uniform(0, pop_size-1)))
        idx_2 = int(round(random.uniform(0, pop_size-1)))
        new_encoding_values = crossover(old_population[idx_1]["encoding"], old_population[idx_2]["encoding"])  
        new_encoding = create_encoding_obj(graph, new_encoding_values, path_options)
        new_population.append(new_encoding)

        new_encoding_values = crossover(old_population[idx_2]["encoding"], old_population[idx_1]["encoding"])  
        new_encoding = create_encoding_obj(graph, new_encoding_values, path_options)
        new_population.append(new_encoding)

    for _ in range(5):
        idx = int(round(random.uniform(0, pop_size-1)))
        new_encoding_values= mutate(old_population[idx]["encoding"])
        new_encoding = create_encoding_obj(graph, new_encoding_values, path_options)
        new_population.append(new_encoding)

    for _ in range(5):
        new_encoding_values= get_random_encoding(encoding_size)
        new_encoding = create_encoding_obj(graph, new_encoding_values, path_options)
        new_population.append(new_encoding)

    new_population = sorted(new_population, key=lambda x: x["cost"], reverse=True)
    size = len(new_population)
    return new_population[size-11: -1]
    


def do_generation(graph, population, path_options, depth = 0):
    cost = get_cost(graph, population[9]["encoding"], path_options)
    print('Current best: ', cost)
    if cost <= 17 or depth > 10000:
        print('DONE')
        return population[9]["encoding"]
    else:
        new_population = get_new_population(graph, population, path_options)
        do_generation(graph, new_population, path_options, depth +1)
    pass


def get_decision_index(arr):
    return int(2 * arr[0] + arr[1])

def get_cost(graph, encoding, path_options):
    nodes = graph.nodes()
    edges_in = {}
    edges_out = {}

    idx = 0
    for s in nodes:
        for d in nodes:
            if d != s:
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
                    edges = edges_in
                    if link_start > link_end:
                        edges = edges_out

                    normalized_indizes = np.sort([link_start, link_end])
                    key = 'edge_' + str(normalized_indizes[0]) + '-' + str(normalized_indizes[1])
                    if key in edges:
                        edges[key] = edges[key] +1
                    else:
                        edges[key] = 1
                    
                idx = idx + 1
    
    utilization = 0  

    keys = set().union(edges_in.keys(), edges_out.keys())
    for key in keys:
        u_1 = 0
        u_2 = 0
        if key in edges_in:
            u_1 = edges_in[key] / 4
        if key in edges_out:
            u_2 = edges_out[key] / 4
            
        link_utilization = max(u_1, u_2)

        utilization = max(link_utilization, utilization)
    return utilization


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
            if d != s:
                name = 'path_' + str(s) + '-' + str(d)
                path_options[name] = list(nx.all_simple_paths(G, source=s, target=d))

    print('Number of pathes ', len(path_options))

    population = []

    # initialize with random decision
    for _ in range(10):
        # 2 bit as decision for every encoding
        encoding_values = get_random_encoding(2 * len(path_options))
        encoding = create_encoding_obj(G, encoding_values, path_options)

        population.append(encoding)
        population = sorted(population, key=lambda x: x["cost"], reverse=True)

    do_generation(G, population, path_options)
    pass


run_genetic_algorithm()
