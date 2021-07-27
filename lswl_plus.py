import networkx as nx
from copy import deepcopy
import os.path
import time
import random
import argparse


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


def create_argument_parser_main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--strength_type", help="1 for weights in [-1,+1] and 2 for weights in [0,1], default is 2.")
	parser.add_argument("-n", "--network", help="network file address")
	parser.add_argument("-i", "--outlier", help="y/n, if outliers need to merge into communities, default is 'y'.")
	parser.add_argument("-c", "--overlap", help="y/n, if overlapping communities need to be detected, default is 'n'.")
	parser.add_argument("-o", "--output", help="path of the output file, default is './community.dat'.")
	return parser.parse_args()


class LSWLPlusCommunityDetection():
	minimum_improvement = 0.000001
	def __init__(self, graph, strength_type, merge_outliers, detect_overlap, nodes_to_ignore=set()):
		self.graph = graph
		self.graph_copy = deepcopy(self.graph)
		self.strength_type = strength_type
		self.merge_outliers = merge_outliers
		self.detect_overlap = detect_overlap
		self.starting_node = None
		self.community = []
		self.shell = set()
		self.nodes_to_ignore = nodes_to_ignore
		self.partition = []
		self.remove_self_loops()
		self.dict_common_neighbors = {}
		self.max_common_neighbors = {}
		self.strength_assigned_nodes = set()
		self.proccessed_nodes = set()

	def reset(self):
		self.community.clear()
		self.shell.clear()

	def remove_self_loops(self):
		for node in self.graph.nodes():
			if self.graph.has_edge(node, node):
				self.graph.remove_edge(node, node)

	def set_start_node(self, start_node):
		self.starting_node = start_node
		self.community.append(start_node)
		self.shell = set(self.graph.neighbors(start_node))
		for node in self.nodes_to_ignore:
			self.shell.discard(node)

	def update_sets_when_node_joins(self, node):
		self.community.append(node)
		self.update_shell_when_node_joins(node)

	def update_shell_when_node_joins(self, new_node):
		self.shell.update(self.graph.neighbors(new_node))
		for node in self.community:
			self.shell.discard(node)
		for node in self.nodes_to_ignore:
			self.shell.discard(node)

	def update_dicts_of_common_neighbors_info(self, node):
		if (node in self.dict_common_neighbors) is False:
			self.dict_common_neighbors[node] = {}
			self.max_common_neighbors[node] = -1

		for neighbor in self.graph.neighbors(node):
			if (neighbor in self.dict_common_neighbors[node]) is False:
				if (neighbor in self.dict_common_neighbors) is False:
					self.dict_common_neighbors[neighbor] = {}
					self.max_common_neighbors[neighbor] = -1

				number_common_neighbors = sum(1 for _ in nx.common_neighbors(self.graph, node, neighbor))
				self.dict_common_neighbors[node][neighbor] = number_common_neighbors
				self.dict_common_neighbors[neighbor][node] = number_common_neighbors

				if number_common_neighbors > self.max_common_neighbors[node]:
					self.max_common_neighbors[node] = number_common_neighbors
				if number_common_neighbors > self.max_common_neighbors[neighbor]:
					self.max_common_neighbors[neighbor] = number_common_neighbors

	def assign_local_strength(self, node):
		if node in self.strength_assigned_nodes:
			return

		self.update_dicts_of_common_neighbors_info(node)
		max_mutual_node = self.max_common_neighbors.get(node)

		for neighbor in self.graph.neighbors(node):
			max_mutual_neighbor = self.max_common_neighbors.get(neighbor)
			strength = self.dict_common_neighbors.get(node).get(neighbor)
			try:
				s1 = strength / max_mutual_node
			except ZeroDivisionError:
				s1 = 0.0
			try:
				s2 = strength / max_mutual_neighbor
			except ZeroDivisionError:
				s2 = 0.0

			strength = s1 + s2 - 1.0 if self.strength_type == 1 else (s1 + s2) / 2.0
			self.graph.add_edge(node, neighbor, strength=strength)
		self.strength_assigned_nodes.add(node)

	def find_best_next_node(self, improvements):
		new_node = self.community[-1]
		for node in self.shell:
			if (node in improvements) is False:
				improvements[node] = self.graph[node][new_node].get('strength', 0.0)
			elif self.graph.has_edge(node, new_node):
				improvements[node] += self.graph[node][new_node].get('strength', 0.0)
		if new_node in improvements:
			del improvements[new_node]

		best_candidate = None
		best_improvement = -float('inf')
		for candidate in self.shell:
			if improvements[candidate] > best_improvement:
				best_candidate = candidate
				best_improvement = improvements[candidate]

		return best_candidate, best_improvement

	def merge_dangling_nodes(self):
		neighborhood = set()
		for node in self.community:
			for neighbor in self.graph.neighbors(node):
				if (neighbor in self.nodes_to_ignore) is False:
					neighborhood.add(neighbor)

		dangling_neighbors = [node for node in neighborhood if self.graph.degree[node] == 1]
		self.community = list(set(self.community + dangling_neighbors))

	def find_community(self, start_node=None):
		if start_node == None:
			remaining_nodes = set(self.graph.nodes() - self.proccessed_nodes)
			start_node = random.choice(list(remaining_nodes))
		self.set_start_node(start_node)
		self.assign_local_strength(self.starting_node)

		improvements = {}
		while len(self.community) < self.graph.number_of_nodes() and len(self.shell) > 0:
			for node in self.shell:
				self.assign_local_strength(node)

			new_node, improvement = self.find_best_next_node(improvements)
			if self.strength_type == 1 and improvement < LSWLPlusCommunityDetection.minimum_improvement:
				break

			if self.strength_type == 2:
				if len(self.community) > 3 and improvement < 1.0 + LSWLPlusCommunityDetection.minimum_improvement:
					break
				elif len(self.community) < 3 and improvement <  LSWLPlusCommunityDetection.minimum_improvement:
					break

			self.update_sets_when_node_joins(new_node)
		if self.merge_outliers == True:
			self.merge_dangling_nodes()

		for node in self.community:
			self.proccessed_nodes.add(node)

		if self.detect_overlap == False:
			for node in self.community:
				self.nodes_to_ignore.add(node)

		self.partition.append(sorted(self.community))   # sort is only for a better representation, can be ignored to boost performance.
		self.reset()

	def community_detection(self):
		while len(self.proccessed_nodes) < self.graph_copy.number_of_nodes():
			self.find_community()				
		
		self.nodes_to_ignore.clear()
		if self.merge_outliers == True:
			self.amend_partition()
		return sorted(self.partition)

	def amend_partition(self):
		communities = [community for community in self.partition if len(community) in [1, 2]]

		for community in communities:
			self.partition.remove(community)

		self.amend_partition_helper(communities)

	def amend_partition_helper2(self, community, strength_dict):
		index_best_community_to_merge_into = list(strength_dict.keys())[0]
		for index_community in strength_dict:
			if strength_dict[index_community] > strength_dict[index_best_community_to_merge_into]:
				index_best_community_to_merge_into = index_community
		for node in community:
			if (node in self.partition[index_best_community_to_merge_into]) is False:
				self.partition[index_best_community_to_merge_into].append(node)
		self.partition[index_best_community_to_merge_into].sort()

	def amend_partition_helper(self, communities):
		for community in communities:
			neighbors = set()
			for node in community:
				neighbors.update(self.graph_copy.neighbors(node))

			strength_dict = {}
			for neighbor in neighbors:
				for i in range(len(self.partition)):
					if neighbor in self.partition[i]:
						for node_in_com in community:
							if self.graph_copy.has_edge(node_in_com, neighbor):
								strength_dict[i] = strength_dict.get(i, 0.0) + self.graph_copy[node_in_com][neighbor].get('weight', 0.0)
						break
			if len(strength_dict) > 0:
				self.amend_partition_helper2(community, strength_dict)
			else:
				self.partition.append(community)

if __name__ == "__main__":
	start_time = time.time()
	
	args = create_argument_parser_main()

	graph = load_graph(args.network)
	strength_type = 1 if args.strength_type == '1' else 2
	merge_outliers = False if args.outlier == 'n' else True
	detect_overlap = True if args.overlap == 'y' else False
	output = args.output if args.output != None else 'community.dat'

	community_detector = LSWLPlusCommunityDetection(deepcopy(graph), strength_type, merge_outliers, detect_overlap)
	partition = community_detector.community_detection()

	with open(output, 'w') as file:
		for e, com in enumerate(partition):
			file.write(str(com) + ' (' + str(len(com)) + ')\n')
		
	print('elapsed time =', time.time() - start_time)
