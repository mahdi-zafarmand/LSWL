import networkx as nx
import os.path
import time
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
	parser.add_argument("-t", "--timeout", help="maximum time for LSWL to recover the community in seconds, default is 2 seconds.")
	parser.add_argument("-o", "--output", help="path of the output file, default is './community.dat'.")
	return parser.parse_args()


class LSWLCommunityDiscovery():
	minimum_improvement = 0.000001
	def __init__(self, graph, strength_type, timeout):
		# initializes the object
		self.graph = graph
		self.strength_type = strength_type
		self.starting_node = None
		self.community = []
		self.shell = set()
		self.remove_self_loops()
		self.dict_common_neighbors = {}
		self.max_common_neighbors = {}
		self.strength_assigned_nodes = set()
		self.timer_timeout = timeout

	def reset(self):
		self.community.clear()
		self.shell.clear()

	def remove_self_loops(self):
		for node in self.graph.nodes():
			if self.graph.has_edge(node, node):
				self.graph.remove_edge(node, node)

	def set_start_node(self, start_node):
		if start_node in self.graph.nodes():
			self.starting_node = start_node
			self.community.append(start_node)
			self.shell = set(self.graph.neighbors(start_node))
		else:
			print('Invalid starting node! Try with another one.')
			exit(-1)

	def update_sets_when_node_joins(self, node):
		self.community.append(node)
		self.update_shell_when_node_joins(node)

	def update_shell_when_node_joins(self, new_node):
		self.shell.update(self.graph.neighbors(new_node))
		for node in self.community:
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
				neighborhood.add(neighbor)

		dangling_neighbors = [node for node in neighborhood if self.graph.degree[node] == 1]
		self.community = list(set(self.community + dangling_neighbors))

	def amend_small_communities(self):
		if len(self.community) < 3:
			if len(self.shell) > 0:
				start_node_for_amend = max(self.shell, key=self.graph.degree)
				next_community_searcher = LSWLCommunityDiscovery(self.graph, self.strength_type, self.timer_timeout)
				new_members = next_community_searcher.community_search(start_node_for_amend, amend=False)
				for new_member in new_members:
					if (new_member in self.community) is False:
						self.community.append(new_member)

	def community_search(self, start_node, amend=True):
		start_timer = time.time()
		self.set_start_node(start_node)
		self.assign_local_strength(self.starting_node)

		improvements = {}
		while len(self.community) < self.graph.number_of_nodes() and len(self.shell) > 0:
			if time.time() > start_timer + self.timer_timeout:
				print('Timeout!')
				return []
				
			for node in self.shell:
				self.assign_local_strength(node)

			new_node, improvement = self.find_best_next_node(improvements)
			if self.strength_type == 1 and improvement < LSWLCommunityDiscovery.minimum_improvement:
				break

			if self.strength_type == 2:
				if len(self.community) > 3 and improvement < 1.0 + LSWLCommunityDiscovery.minimum_improvement:
					break
				elif len(self.community) < 3 and improvement <  LSWLCommunityDiscovery.minimum_improvement:
					break

			self.update_sets_when_node_joins(new_node)

		if amend:
			self.amend_small_communities()
		self.merge_dangling_nodes()
		return sorted(self.community)	# sort is only for a better representation, can be ignored to boost performance.


if __name__ == "__main__":
	start_time = time.time()
	
	args = create_argument_parser_main()
	graph = load_graph(args.network)
	query_nodes = read_query_nodes(args.query_nodes)
	strength_type = 1 if args.strength_type == '1' else 2
	timeout = float(args.timeout) if args.timeout != None and args.timeout.isnumeric() == True else 2.0
	output = args.output if args.output != None else 'community.dat'

	community_searcher = LSWLCommunityDiscovery(graph, strength_type, timeout)
	with open(output, 'w') as file:
		for e, node_number in enumerate(query_nodes):
			community = community_searcher.community_search(start_node=node_number)
			print(str(e + 1) + ' : ' + str(node_number) + ' > (' + str(len(community)) + ' nodes)')
			file.write(str(node_number) + ' : ' + str(community) + ' (' + str(len(community)) + ')\n')
			community_searcher.reset()

	print('elapsed time =', time.time() - start_time)