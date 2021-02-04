import networkx as nx
import os.path
import time
from random import random


def load_graph(path, weighted=False, delimiter='\t', self_loop=False):
	graph = nx.Graph()
	if not os.path.isfile(path):
		print("Error: file " + path + " not found!")
		exit(-1)

	with open(path) as file:
		for line in file.readlines():
			w = 1.0
			line = line.split(delimiter)
			v1 = int(line[0])
			v2 = int(line[1])
			graph.add_node(v1)
			graph.add_node(v2)

			if weighted:
				w = float(line[2])

			if (self_loop and v1 == v2) or (v1 != v2):
				graph.add_edge(v1, v2, weight=w)

	return graph


class ModularityRCommunityDiscovery():
	# the class to search for the community of a given node in a social network using Local SIWO algorithm.
	minimum_improvement = 0.000001     # if an improvement is less than minimum, the process stops considering stability
	timer_timeout = 2.0

	def __init__(self, graph):
		# initializes the object
		self.graph = graph
		self.starting_node = None
		self.community = []
		self.boundary = set()
		self.shell = set()
		self.remove_self_loops()

	def reset(self):
		# resets the object to prepare it for another use
		self.community.clear()
		self.boundary.clear()
		self.shell.clear()

	def remove_self_loops(self):
		# algorithms tend to work better if there is no self-loop in the given graph, so we call this method at first.
		for node in self.graph.nodes():
			if self.graph.has_edge(node, node):
				self.graph.remove_edge(node, node)

	def set_start_node(self, start_node):
		# check the validity of the given start_node, then puts it in the community and initialize the shell set.
		if start_node in self.graph.nodes():
			self.starting_node = start_node
			self.community.append(start_node)
			self.boundary.add(start_node)
			self.shell = set(self.graph.neighbors(start_node))
		else:
			print('Invalid starting node! Try with another one.')
			exit(-1)

	def update_sets_when_node_joins(self, node, change_boundary=False):
		self.community.append(node)
		if change_boundary:
			self.update_boundary_when_node_joins(node)
		self.update_shell_when_node_joins(node)

	def update_shell_when_node_joins(self, new_node):
		# after a new_node expands the community, the shell set should be updated.
		self.shell.update(self.graph.neighbors(new_node))
		for node in self.community:
			self.shell.discard(node)

	def update_boundary_when_node_joins(self, new_node):
		# after a new_node expands the community, boundary set should be updated by adding and removing some nodes.
		should_be_boundary = False
		for neighbor in self.graph.neighbors(new_node):
			if (neighbor in self.community) is False:
				should_be_boundary = True
				break
		if should_be_boundary:
			self.boundary.add(new_node)

	def find_best_next_node(self, improvements):
		best_candidate = None
		best_improvement = - float('inf')
		for candidate, improvement in sorted(improvements.items(), key=lambda x: random()):
			if improvement > best_improvement:
				best_candidate = candidate
				best_improvement = improvement
		return best_candidate

	def community_search(self, start_node):   # no use for 'with_amend' in this algorithm.
		# THE MAIN FUNCTION OF THE CLASS, finds all other nodes that belong to the same community as the start_node does.
		self.set_start_node(start_node)
		modularity_r = 0.0
		T = self.graph.degree[start_node]

		while len(self.community) < self.graph.number_of_nodes() and len(self.shell) > 0:
			delta_r = {}  # key: candidate nodes from the shell set, value: total improved strength after a node joins.
			delta_T = {}  # key: candidate nodes from the shell set, value: delta T (based on notations of the paper).
			for node in self.shell:
				delta_r[node], delta_T[node] = self.compute_modularity((modularity_r, T), node)

			new_node = self.find_best_next_node(delta_r)
			if delta_r[new_node] < ModularityRCommunityDiscovery.minimum_improvement:
				break

			modularity_r += delta_r[new_node]
			T += delta_T[new_node]
			self.update_sets_when_node_joins(new_node, change_boundary=True)

		return sorted(self.community)   # sort is only for a better representation, can be ignored to boost performance.

	def compute_modularity(self, auxiliary_info, candidate_node):
		R, T = auxiliary_info
		x, y, z = 0, 0, 0
		for neighbor in self.graph.neighbors(candidate_node):
			if neighbor in self.boundary:
				x += 1
			else:
				y += 1

		for neighbor in [node for node in self.graph.neighbors(candidate_node) if node in self.boundary]:
			if self.should_leave_boundary(neighbor, candidate_node):
				for node in self.graph.neighbors(neighbor):
					if (node in self.community) and ((node in self.boundary) is False):
						z += 1
		return float(x - R * y - z * (1 - R)) / float(T - z + y), -z + y

	def should_leave_boundary(self, possibly_leaving_node, neighbor_node):
		# to find if 'possibly_leaving_node' should leave 'self.boundary' because of the agglomeration of 'neighbor_node'.
		neighbors = set(self.graph.neighbors(possibly_leaving_node))
		neighbors.discard(neighbor_node)
		for neighbor in neighbors:
			if (neighbor in self.community) is False:
				return False
		return True

def read_query_nodes(filename):
	query_nodes = []
	with open(filename, 'r') as file:
		lines = file.readlines()
		for i in range(len(lines)):
			query_nodes.append(int(lines[i].split()[0]))
	return query_nodes


if __name__ == "__main__":
	start_time = time.time()
	
	network_file_address = 'karate_edge_list.txt'
	query_nodes_filename = 'query_nodes.txt'

	graph = load_graph(network_file_address)
	query_nodes = read_query_nodes(query_nodes_filename)

	community_searcher = ModularityRCommunityDiscovery(graph)
	with open('mod_r_results.txt', 'w') as file:
		for e, node_number in enumerate(query_nodes):
			print(str(e) + ' : ' + str(node_number) + ' > (', end='')
			community = community_searcher.community_search(start_node=node_number)
			print(str(len(community)) + ' nodes)')
			file.write(str(node_number) + ' : ' + str(community) + ' (' + str(len(community)) + ')\n')
			community_searcher.reset()

	print('elapsed time =', time.time() - start_time)