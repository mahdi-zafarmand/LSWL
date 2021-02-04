import networkx as nx
import os.path
import time
from random import random, shuffle


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


class ModularityMCommunityDiscovery():
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

	def update_sets_when_node_leaves(self, node, change_boundary=False):
		self.community.remove(node)
		if change_boundary:
			self.update_boundary_when_node_leaves(node)
		self.update_shell_when_node_leaves(node)

	def update_boundary_when_node_leaves(self, old_node):
		if old_node in self.boundary:
			self.boundary.remove(old_node)
			for node in self.graph.neighbors(old_node):
				if node in self.community:
					self.boundary.add(node)

	def update_shell_when_node_leaves(self, old_node):
		possibles_leaving_nodes = [node for node in self.graph.neighbors(old_node) if node in self.shell]
		for node in possibles_leaving_nodes:
			should_leave_shell = True
			for neighbor in self.graph.neighbors(node):
				if neighbor in self.community:
					should_leave_shell = False
					break
			if should_leave_shell:
				self.shell.remove(node)
		self.shell.add(old_node)

	def community_search(self, start_node, with_amend=False):  # no use for 'with_amend' in this algorithm.
		# THE MAIN FUNCTION OF THE CLASS, finds all other nodes that belong to the same community as the start_node does.
		self.set_start_node(start_node)
		sorted_shell = list(self.shell)

		modularity = 0.0
		while len(self.community) < self.graph.number_of_nodes() and len(self.shell) > 1:
			# addition step
			Q_list = []
			sorted_shell.sort(key=self.graph.degree)
			for candidate_node in sorted_shell:
				new_modularity = self.compute_modularity('addition', candidate_node)
				if new_modularity > modularity:
					modularity = new_modularity
					self.update_sets_when_node_joins(candidate_node)
					sorted_shell.remove(candidate_node)
					Q_list.append(candidate_node)

			while True:
				# deletion step
				Q_delete = []
				for candidate_node in sorted(self.community, key=lambda x: random()):
					new_modularity = self.compute_modularity('deletion', candidate_node)
					if new_modularity > modularity:
						modularity = new_modularity
						self.update_sets_when_node_leaves(candidate_node)
						Q_delete.append(candidate_node)

						if candidate_node in Q_list:
							Q_list.remove(candidate_node)

				if len(Q_delete) == 0:
					break

			for node in sorted(Q_list, key=lambda x: random()):
				neighbors = list(self.graph.neighbors(node))
				shuffle(neighbors)
				for neighbor in neighbors:
					if (neighbor in self.community) is False:
						self.shell.add(neighbor)
						if (neighbor in sorted_shell) is False:
							sorted_shell.append(neighbor)

			if len(Q_list) == 0:
				break

		if self.starting_node in self.community:
			return sorted(self.community)
		return []

	def compute_modularity(self, auxiliary_info, candidate_node):
		mode = auxiliary_info
		ind_s, outd_s = 0, 0

		community = list(self.community)
		if mode == 'addition':
			community.append(candidate_node)
		elif mode == 'deletion':
			community.remove(candidate_node)

		for node in community:
			for neighbor in self.graph.neighbors(node):
				if neighbor in community:
					ind_s += 1
				else:
					outd_s += 1

		return float(ind_s) / float(outd_s)

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

	community_searcher = ModularityMCommunityDiscovery(graph)
	with open('mod_m_results.txt', 'w') as file:
		for e, node_number in enumerate(query_nodes):
			print(str(e) + ' : ' + str(node_number) + ' > (', end='')
			community = community_searcher.community_search(start_node=node_number)
			print(str(len(community)) + ' nodes)')
			file.write(str(node_number) + ' : ' + str(community) + ' (' + str(len(community)) + ')\n')
			community_searcher.reset()

	print('elapsed time =', time.time() - start_time)