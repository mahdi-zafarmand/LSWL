import networkx as nx
import os.path
import time
import argparse
import linecache
import numpy as np


def read_query_nodes(path):
	query_nodes = []
	if not os.path.isfile(path):
		print("Error: file " + path + " not found!")
		exit(-1)

	with open(path, 'r') as file:
		lines = file.readlines()
		for i in range(len(lines)):
			query_nodes.append(int(lines[i]))
	return query_nodes


def create_argument_parser_main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--strength_type", help="1 for weights in [-1,+1] and 2 for weights in [0,1], default is 2.")
	parser.add_argument("-n", "--network", help="network file address")
	parser.add_argument("-q", "--query_nodes", help="query nodes file address")
	parser.add_argument("-t", "--timeout", help="maximum time for LSWL to recover the community in seconds, default is 1 second.")
	parser.add_argument("-o", "--output", help="path of the output file, default is './community.dat'.")
	return parser.parse_args()


class OnlineCommunitySearch:
	minimum_improvement = 0.000001
	def __init__(self, adj_list_address, strength_type, timeout):
		self.graph = nx.Graph()
		self.adj_list_address = adj_list_address
		self.strength_type = strength_type
		self.nodes_in_graph = set()
		self.community = []
		self.shell = set()
		self.strength_assigned_nodes = set()
		self.dict_common_neighbors = {}
		self.max_common_neighbors = {}
		self.timer_timeout = timeout

	def add_edges_before_strength_assignment(self):
		d = {}
		for node in self.shell:
			d[node] = self.read_neighbors(node)

			for neigh in d[node]:
				if (neigh in d) is False:
					d[neigh] = self.read_neighbors(neigh)

		for key, value in d.items():
			self.add_new_edges(key, value)

	def add_edge_weights(self, new_node, edge_weights):
		for edge in self.graph.edges(new_node):
			if edge[1] in self.community:
				edge_weights.append((new_node, edge[1], self.graph[new_node][edge[1]].get('strength', 0.0)))

	def remove_nodes(self, main_node, edge_weights):
		if edge_weights == []:
			return

		edge_weights.sort(key=lambda x:x[2])
		quartile = np.quantile(edge_weights, 0.25)

		remaining_nodes, length = set([main_node]), 1
		while True:
			for n1, n2, w in edge_weights:
				if w >= quartile and n1 in remaining_nodes:
					remaining_nodes.add(n1)
				elif w >= quartile and n2 in remaining_nodes:
					remaining_nodes.add(n1)
			if len(remaining_nodes) == length:
				break
			length = len(remaining_nodes)

		self.community = list(remaining_nodes)

	def community_search(self, start_node, amend=True):
		start_timer = time.time()
		self.initilize(start_node)

		improvements, edge_weights = {}, list()
		while len(self.community) < self.graph.number_of_nodes() and len(self.shell) > 0:
			if time.time() > start_timer + self.timer_timeout:
				print('Timeout!')
				break

			self.add_edges_before_strength_assignment()
			for node in self.shell:
				self.assign_local_strength(node)

			new_node, improvement = self.find_best_next_node(improvements)
			if self.strength_type == 1 and improvement < OnlineCommunitySearch.minimum_improvement:
				break

			if self.strength_type == 2:
				if len(self.community) > 3 and improvement < 1.0 + OnlineCommunitySearch.minimum_improvement:
					break
				elif len(self.community) < 3 and improvement <  OnlineCommunitySearch.minimum_improvement:
					break

			self.add_edge_weights(new_node, edge_weights)
			self.update_sets_when_node_joins(new_node)

		self.remove_nodes(start_node, edge_weights)

		if amend:
			self.amend_small_communities()
		self.merge_dangling_nodes()
		return sorted(self.community)   # sort is only for a better representation, can be ignored to boost performance.

  
	def read_neighbors(self, node):
		neighbors = []
		line = linecache.getline(self.adj_list_address, node)
		striped_line = line.split()
		if len(striped_line) > 0 and int(striped_line[0]) == node:
			for x in striped_line[1:]:
				neighbors.append(int(x))
		return neighbors

	def real_degree(self, node):
		return len(self.read_neighbors(node))

	def add_new_edges(self, main_node, neighbors):
		for i in range(len(neighbors)):
			self.graph.add_edge(main_node, neighbors[i])
   
	def initilize(self, start_node):
		self.graph.add_node(start_node)
		self.community.append(start_node)
		neighbors = self.read_neighbors(start_node)
		self.add_new_edges(start_node, neighbors)
		self.shell.update(neighbors)  
		self.add_edges_before_strength_assignment()
		self.assign_local_strength(start_node)
  
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
			if candidate == new_node:
				continue
			if improvements[candidate] > best_improvement:
				best_candidate = candidate
				best_improvement = improvements[candidate]

		return best_candidate, best_improvement

	def update_sets_when_node_joins(self, node, change_boundary=False):
		self.community.append(node)
		self.update_shell_when_node_joins(node)

	def update_shell_when_node_joins(self, new_node):
		self.shell.update(self.graph.neighbors(new_node))
		for node in self.community:
			self.shell.discard(node)

	def merge_dangling_nodes(self):
		neighborhood = set()
		dangling_neighbors = []
		for node in self.community:
			for neighbor in self.read_neighbors(node):
				neighborhood.add(neighbor)

		dangling_neighbors = [node for node in neighborhood if self.real_degree(node) == 1]
		self.community = list(set(self.community + dangling_neighbors))

	def amend_small_communities(self):
		if len(self.community) < 3:
			if len(self.shell) > 0:
				start_node_for_amend = max(self.shell, key=self.real_degree)
				next_community_searcher = OnlineCommunitySearch(self.adj_list_address, self.strength_type, self.timer_timeout)
				new_members = next_community_searcher.community_search(start_node_for_amend, amend=False)
				for new_member in new_members:
					if (new_member in self.community) is False:
						self.community.append(new_member)


if __name__ == '__main__':
	start_time = time.time()

	args = create_argument_parser_main()
	query_nodes = read_query_nodes(args.query_nodes)
	strength_type = 1 if args.strength_type == '1' else 2
	timeout = float(args.timeout) if args.timeout != None and args.timeout.isnumeric() == True else 1.0
	output = args.output if args.output != None else 'community.dat'
	
	with open(output, 'w') as file:
		for e, node_number in enumerate(query_nodes):
			community_searcher = OnlineCommunitySearch(args.network, strength_type, timeout)
			community = community_searcher.community_search(node_number)
			print(str(e + 1) + ' : ' + str(node_number) + ' > (' + str(len(community)) + ' nodes)')
			file.write(str(node_number) + ' : ' + str(community) + ' (' + str(len(community)) + ')\n')
			del community_searcher
	print('elapsed time =', time.time() - start_time)
