import networkx as nx
import numpy
import matplotlib.pyplot as plot
import itertools
from random import randint
import argparse
import math

verbose = False

# Returns the number of cables installed on a link.
def get_installed_cables(G, node1, node2, type):
    return G[node1][node2]["cable_type_" + str(type)]

def verbose_print(string):
	if verbose:
		print(string)

# Returns the total capacity on a link in the graph.
def get_capacity(G, node1, node2, capacities):
    capacity = 0
    # Go through all link types.
    for link in range(0, len(capacities)):
        num_cables_of_type = get_installed_cables(G, node1, node2, link)
        capacity_of_type = num_cables_of_type * capacities[link]
        capacity = capacity + capacity_of_type
    return capacity

# Returns a vector with the respective number of cables required per type to satisfy the target capacity.
def get_required_cables(target_capacity, capacities):
    cables = [0 for i in range(0, len(capacities))]
    for i in reversed(range(0, len(capacities))):
        capacity = capacities[i]
        while capacity <= target_capacity:
            cables[i] = cables[i] + 1
            target_capacity = target_capacity - capacity
    return cables

def get_cost(cables, costs):
    cost = 0
    for cable in range(0, len(cables)):
        cost = cost + costs[cable] * cables[cable]
    return cost

def install_cables(G, i, j, cable_type, num_cables, capacities):
    if (num_cables == 0):
        return
    G[i][j]["cable_type_" + str(cable_type)] = G[i][j]["cable_type_" + str(cable_type)] + num_cables
    G[i][j]["capacity"] = get_capacity(G, i, j, capacities)

def add_utilized_capacity(G, i, j, used_capacity):
    G[i][j]["utilized_capacity"] = G[i][j]["utilized_capacity"] + used_capacity
    G[i][j]["unutilized_capacity"] = G[i][j]["capacity"] - G[i][j]["utilized_capacity"]

def solve(demandMat, G, capacities, costs, demandIndexPairs):
	n = len(G.nodes)
	routeAssignmentMat = [[None for i in range(0, n)] for i in range(0, n)]
	total_cost = 0
	for pair in demandIndexPairs:
		i = pair[0]
		j = pair[1]
		# Demand for node pair (i, j).
		demand = demandMat[i, j]
		minimal_cost = None
		best_path = None
		best_cables = None
		verbose_print("Checking demand " + str(i) + " <-- " + str(demand) + " --> " + str(j))
		# Find all paths i->j
		paths = nx.all_simple_paths(G, i, j)
		for path in paths:
			verbose_print("\tPath " + str(path) + ":")
			path_cost = 0
			required_cables = None
			# Go through each segment of the path.
			for node in range(0, len(path) - 1):
				n1 = path[node]
				n2 = path[node + 1]
				# The required cables to fulfill a target demand of 'demand - free capacity'.
				required_cables = get_required_cables(demand - G[n1][n2]["unutilized_capacity"], capacities)
				# The segmnet cost.
				segment_cost = get_cost(required_cables, costs)
				# Total path cost.
				path_cost = path_cost + segment_cost
				verbose_print("\t\tSegment [" + str(n1) + " " + str(n2) + "] requires " + str(required_cables) + " cables at cost of " + str(segment_cost))
			verbose_print("\t\ttotal cost is " + str(path_cost))
			# If the current path is cheaper than the last best one (or this is the first one we're investigating), then remember it.
			if minimal_cost is None or path_cost < minimal_cost:
				minimal_cost = path_cost
				best_path = path
				best_cables = required_cables
		# Have found best path.
		verbose_print("\t=> Best path is " + str(best_path) + " at cost " + str(minimal_cost) + " where cables " + str(best_cables) + " are installed.")
		for node in range(0, len(best_path) - 1):
			n1 = best_path[node]
			n2 = best_path[node + 1]
			# Install cables on each segment.
			for cable in range(0, len(best_cables)):
				install_cables(G, n1, n2, cable, best_cables[cable], capacities)
			# Update link capacities.
			add_utilized_capacity(G, n1, n2, demand)
		# Having installed cables, remember the best path and update the global cost.
		routeAssignmentMat[i][j] = best_path
		total_cost = total_cost + minimal_cost
	return routeAssignmentMat, G, total_cost

def print_results(G, n, edges, demandMat, routeAssignmentMat, total_cost):
	print("Link\tCables")
	for i in range(0, n):
	    for j in range(i + 1, n):
	        if [i,j] in edges:
	            print(str(i) + " - " + str(j) + "\t" + str(G[i][j]))
	print("Total cost: " + str(total_cost))
	print("Node pair\tDemand\tRoute assignment")
	for i in range(0, n):
	    for j in range(i + 1, n):
	        print("(" + str(i) + ", " + str(j) + ")\t\t" + str(demandMat[i][j]) + "\t" + str(routeAssignmentMat[i][j]))

def plot_graph(G, n):
	pos = nx.spring_layout(G)
	nx.draw(G, pos, with_labels = True)

	# Construct edge labels as strings.
	labels = nx.get_edge_attributes(G, 'cable_type_0')
	for i in range(1, n):
	    current_labels = nx.get_edge_attributes(G, "cable_type_" + str(i))
	    for key in labels.keys():
	        if key in current_labels.keys():
	            labels[key] = str(labels[key]) + "," + str(current_labels[key])

	nx.draw_networkx_edge_labels(G, pos, edge_labels = labels)
	plot.show()

def parse_edge(string):
	pair = string.split(",")
	edge = [int(pair[0]), int(pair[1])]
	return edge

def parse_demand(string):
	split_1 = string.split(",")
	split_2 = split_1[1].split(":")
	i = split_1[0]
	j = split_2[0]
	demand = split_2[1]
	return [int(i), int(j), int(demand)]

def parse_bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_commandline():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--costs",
		nargs = "*",
		type=int
		)

	parser.add_argument(
		"--capacities",
		nargs = "*",
		type=int
		)

	parser.add_argument(
		"--edges",
		nargs = "*",
		type = parse_edge
		)

	parser.add_argument(
		"--num_iterations",
		default = 1,
		type = int
		)

	parser.add_argument(
		"--demands",
		nargs = "*",
		type = parse_demand
		)
	parser.add_argument(
		"--verbose",
		type = parse_bool,
		nargs = "?",
		const = True,
		default = "0"
	)

	args = parser.parse_args()

	if not args.costs or len(args.costs) == 0:
		raise ValueError("You need to specify the costs vector with --costs 1 2 3 4")

	if not args.capacities or len(args.capacities) == 0:
		raise ValueError("You need to specify the capacities vector with --capacities 1 2 3 4")

	if not len(args.costs) == len(args.capacities):
		raise ValueError("Need equally many costs and capacities!")

	if not args.edges or len(args.edges) == 0:
		raise ValueError("You need to specify the edges with --edges 0,1 0,2 0,3 1,3 2,3")

	if not args.demands or len(args.demands) == 0:
		raise ValueError("You need to specify the demands with --demands 0,1:5 to set a demand of 5 between nodes 0 and 1. Unprovided demands default to 0.")

	global verbose
	verbose = args.verbose	

	return args

def main():
	args = parse_commandline()
	# We have some cost associated to each link type.
	costs = args.costs
	# And a capacity that goes with it.
	capacities = args.capacities

	# Create the graph.
	edges = args.edges #[[0,1], [0,2], [0,3], [1,3], [2,3]]
	G = nx.Graph()
	for e in edges:
		G.add_edge(e[0], e[1])
		for link in range(0, len(capacities)):
			G[e[0]][e[1]]["cable_type_" + str(link)] = 0
		G[e[0]][e[1]]["capacity"] = 0
		G[e[0]][e[1]]["utilized_capacity"] = 0
		G[e[0]][e[1]]["unutilized_capacity"] = 0

	if min(G.nodes) != 0:
		raise ValueError("This implementation requires node indices to start at 0, but your smallest node index is '" + str(min(G.node)) + "'.")

	# Create the demand matrix.
	n = len(G.nodes)
	demandMat = numpy.zeros((n, n))
	for i in range(0, n):
		for j in range(i+1, n):
			demandMat[i, j] = 0

	for pos in range(0, len(args.demands)):
		i = args.demands[pos][0]
		j = args.demands[pos][1]
		demand = args.demands[pos][2]
		demandMat[i, j] = demand

	for i in range(0, n):
	    for j in range(i, n):
	        demandMat[j, i] = demandMat[i, j]

	# The pairs (i,j) determien the order in which demands are processed.
	demandIndexPairs = []

	for i in range(0, n):
	    for j in range(i + 1, n):
	    	demandIndexPairs.append([i, j])

	num_iterations = args.num_iterations

	best_routeAssignmentMat = None
	best_G = None
	best_total_cost = float('inf')
	for i in range(0, num_iterations):
		swap_i = randint(0, len(demandIndexPairs) - 1)
		swap_j = randint(0, len(demandIndexPairs) - 1)
		while swap_j == swap_i:
			swap_j = randint(0, len(demandIndexPairs) - 1)
		tmp = demandIndexPairs[swap_i]
		demandIndexPairs[swap_i] = demandIndexPairs[swap_j]
		demandIndexPairs[swap_j] = tmp

		print("\nIteration " + str(i+1) + " / " + str(num_iterations))
		# Solve the problem, and obtain the route assignment matrix (demand -> route).

		current_routeAssignmentMat, current_G, current_total_cost = solve(demandMat, G.copy(), capacities, costs, demandIndexPairs)
		print("Total cost: " + str(current_total_cost))
		if current_total_cost < best_total_cost:
			print("Updating best solution.")
			best_routeAssignmentMat = current_routeAssignmentMat
			best_G = current_G
			best_total_cost = current_total_cost

	# Print results.
	print("\n\nBest result after " + str(num_iterations) + " iterations:")
	print_results(best_G, n, edges, demandMat, best_routeAssignmentMat, best_total_cost)

	# Plot results.
	plot_graph(best_G, len(costs))

if __name__ == "__main__":
	main()
