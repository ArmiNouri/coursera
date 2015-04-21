#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from sets import Set

from collections import namedtuple
Edge = namedtuple("Edge", ['source', 'dest', 'dist'])


#node object
class Node:
	def __init__(self, nm):
		self.name = nm
		self.label = None
		self.adjacent = {}
	def __str__(self):
		return 'Node ({n}, {l}) - neighbors: {a}'.format(n = self.name, l = self.label, a = self.adjacent)
	def __repr__(self):
		return "Node(%s)" % (self.name)
	def __eq__(self, other):
		if isinstance(other, Node):
			return (self.name == other.name)
		else:
			return False
	def __ne__(self, other):
		return (not self.__eq__(other))
	#hash function for maintaining uniqueness in Set	
	def __hash__(self):
		return hash(self.__repr__())

class Graph:
	def __init__(self, nc, ec):
		self.node_count = nc	
		self.edge_count = ec
		self.nodes = {}	
		self.incoming_edges = {}
	

def solve_it(input_data):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	node_count = int(firstLine[0])
	line_count = int(firstLine[1])

	graph = Graph(node_count, line_count)
	for i in range(1, line_count+1):
		line = lines[i]
		parts = line.split()
		source = Node(int(parts[0]))
		dest = Node(int(parts[1]))
		dist = int(parts[2])
		if source.name in graph.nodes:
			source = graph.nodes[source.name]
		source.adjacent[dest.name] = dist
		graph.nodes[source.name] = source
		if dest.name in graph.nodes:
			dest = graph.nodes[dest.name]
		graph.nodes[dest.name] = dest
		# add edges in reverse (i.e. incoming) order to the graph for easy referral during the bellman-ford run
		dest_edges = {}
		if dest.name in graph.incoming_edges:
			dest_edges = graph.incoming_edges[dest.name]
		dest_edges[source.name]	= dist
		graph.incoming_edges[dest.name] = dest_edges
		

	
	# prepare graph for the bellman-ford algorithm
	# add a node with distance 0 to all nodes in the graph
	dummy = Node(0)
	for n in graph.nodes:
		dummy.adjacent[n] = 0
	# graph.nodes[dummy.name] = dummy	
	for dest in graph.nodes:
		if dest not in graph.incoming_edges:
			graph.incoming_edges[dest] = {}
		graph.incoming_edges[dest][dummy.name] = 0	

	# run bellman-ford once
	matrix = [[0 for x in range(graph.node_count + 1)] for x in range(graph.node_count + 1)]

	# set source (dummy)'s distance to zero, all other nodes' to +inf
	matrix[0][dummy.name] = 0
	for v in graph.nodes:
		matrix[0][v] = sys.maxint

	# iterate through sub-problems
	for i in range(1, graph.node_count + 1):
		for v in graph.nodes:
			print i,'\t',v
			case_one = matrix[i-1][v]
			case_two = sys.maxint
			vees = graph.incoming_edges[v]
			for incoming_v in vees:
				if matrix[i-1][incoming_v] + vees[incoming_v] < case_two:
					case_two = matrix[i-1][incoming_v] + vees[incoming_v]	
			out = case_one if case_one < case_two else case_two				
			matrix[i][v] = out


	# check for negative cycles:
	for v in graph.nodes:
		if matrix[graph.node_count - 1][v] != matrix[graph.node_count][v]:
			return None					


	# label each node with its shortest path distance						
	for n in graph.nodes:
		graph.nodes[n].label = matrix[graph.node_count - 1][n]	

	# boost edge weights accordingly
	edges = []
	for source in graph.nodes:
		for dest in graph.nodes[source].adjacent:
				graph.nodes[source].adjacent[dest] += graph.nodes[source].label - graph.nodes[dest].label
				edge = Edge(source, dest, graph.nodes[source].adjacent[dest])
				edges.append(edge)														

	# run dijkstra's algorithm n times
	edges.sort(key=lambda x: x.dist)
	min_paths = {}
	for v in graph.nodes:
		print v
		unvisited_edges = edges[:]
		visited_nodes = Set([])
		visited_nodes.add(v)
		matx = [sys.maxint for x in range(graph.node_count)]
		matx[v-1] = 0
		while len(visited_nodes) < len(graph.nodes):
			min_edge = None
			min_cost = sys.maxint
			# pick up the first edge which has one end in the visited set and one end in the unvisited set
			# since unvisited_edges are already sorted by cost, the first such edge will be the target edge
			for edge in unvisited_edges:
				if edge.source in visited_nodes and edge.dest not in visited_nodes:
					min_cost = edge.dist
					min_edge = edge	
					break
			# if you failed to find any outgoing edges from the current cut to any unvisited node,
			# it means the current start node doesn't have any paths to any unvisited node		
			if min_edge is None:
				break									
			matx[min_edge.dest - 1] = matx[min_edge.source - 1] + min_cost - graph.nodes[min_edge.source].label + graph.nodes[min_edge.dest].label	
			visited_nodes.add(min_edge.dest)
			unvisited_edges.remove(min_edge)
		# determine the shortes path for the current node
		min_path = sys.maxint	
		min_source = v
		min_dest = None
		for x in range(0, len(matx)):	
			if x != v-1 and matx[x] < min_path:
				min_path = matx[x]
				min_dest = x+1
		min_paths[v] = min_path if min_dest is not None else sys.maxint

	# look up the shortes path in the entire graph:
	min_path = sys.maxint
	for x in min_paths:		
		if min_paths[x] < min_path:
			min_path = min_paths[x]
	return min_path

import sys

if __name__ == '__main__':
	if len(sys.argv) > 1:
		file_location = sys.argv[1].strip()
		input_data_file = open(file_location, 'r')
		input_data = ''.join(input_data_file.readlines())
		input_data_file.close()
		print solve_it(input_data)
	else:
		print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

