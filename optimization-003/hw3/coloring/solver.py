#!/usr/bin/python
# -*- coding: utf-8 -*-
from sets import Set
import copy
import random
import operator
import math

from collections import namedtuple

class ColorClass:
	def __init__(self):
		self.nodes = []
		self.size = 0
		self.clashing_nodes = 0
	def cost(self):
		return 2 * self.size * self.clashing_nodes - math.pow(self.size, 2)	

	def __str__(self):
		return "colorClass: nodes = {ns}, size = {s}, clashing = {cl}".format(ns = self.nodes, s = self.size, cl = self.clashing_nodes) 

#define nodes in the graph
class Node:
	def __init__(self, name):
		self.name = name
		self.neighbors = []
		# this array flags all previsouly discovered cliques so they can be ignored in each new iteration
		self.ignore = []
		self.color = -1
		# this array holds available colors for the node
		self.color_vals = []
		# keep track of how many neghibors fall under each color
		# this makes it easier to keep track of the cost
		# self.neighbor_colors = {}

	def __str__(self):
		out = ""
		for n in self.neighbors:
			out = out + str(n)+ ","
		return "Node(name = {n}, color = {c}, color_range = {r})'s neighbors:".format(n = self.name, c = self.color, r = self.color_vals)+"\n"+out+"\n"

	# choose the next available value in your color set
	def next_color(self):
		if len(self.color_vals) > 0:
			col = self.color_vals[0]
			self.color_vals = self.color_vals[1:]
			return col
		else:
			return -1

	# remove a color value from your set of colors
	def prune_color(self, col):
		if col in self.color_vals:
			self.color_vals.remove(col)	

	def set_max_color(self, color):
		self.color_vals = range(0, color)					

#define graph as a dictionary of nodes
class Graph:
	def __init__(self, nc, ec):
		self.nodes = {}
		self.node_count = nc
		self.edge_count = ec
		self.color_classes = {}
		self.current_cost = sys.maxint
		# initially, the lower bound on the chromatic number of the graph is set to zero
		# later, the largest clique found in the graph will repalce this value
		self.bound = 0

	def __str__(self):
		out = ""
		for nodeName in self.nodes:
			out = out + self.nodes[nodeName].__str__()
		return "Graph(node_count = {nc}, edge_count = {ec}) has these nodes:".format(nc = self.node_count, ec = self.edge_count)+"\n"+out
		
	def set_bound(self, bound):
		self.bound = bound
		for n in self.nodes:
			self.nodes[n].color_vals = list(range(0, self.bound))
			self.nodes[n].color = -1
			self.nodes[n].ignore = [False] * len(self.nodes[n].neighbors)

	def find_max_colors(self):
		maxCols = 0
		for n in self.nodes:
			if self.nodes[n].color > maxCols:
				maxCols = self.nodes[n].color
		return maxCols + 1

	# given a recently colored node, remove its color from the set of legitimate colors from all of its neighbors
	def prune_colors(self, nodeName, nodeColor):
		for n in self.nodes[nodeName].neighbors:
			self.nodes[n].prune_color(nodeColor)

	# pivot-based Bron-Kerbosch algorithm for finding cliques in the graph
	def BronKerbosch(self, R, P, X):
		if len(P) == 0 and len(X) == 0:
			# once you find a clique, mark its edges as 'ignored' so you don't double-count it next time
			for n in self.nodes:
				if self.nodes[n].name in R:
					for i in range(0, len(self.nodes[n].neighbors)):
						if self.nodes[n].neighbors[i] in R:
							self.nodes[n].ignore[i] = True
			return R
		#choose a pivot vertex u in P ⋃ X
		u = P.union(X).pop()
		Nu = Set([])
		for i in range(0, len(self.nodes[u].neighbors)):
			if not self.nodes[u].ignore[i]:
				Nu.add(self.nodes[u].neighbors[i])
		for v in  P - Nu:
			Sv = Set([v])
			Nv = Set([])
			for i in range(0, len(self.nodes[v].neighbors)):
				if not self.nodes[v].ignore[i]:
					Nv.add(self.nodes[v].neighbors[i])
			return self.BronKerbosch(R.union(Sv), P.intersection(Nv), X.intersection(Nv))
			P = P - Sv
			X = X.union(Sv)

	# find a max clique in the graph using Bron-Kerbosch's algorithm
	def next_clique(self):
		R = Set([])
		P = Set([])
		X = Set([])
		for n in self.nodes:
			P.add(self.nodes[n].name)
		clique = self.BronKerbosch(R, P, X)
		return clique

	# given a clique, color it with varying colors
	def color_clique(self, clique, nodes):
		for n in clique:
			if self.nodes[n] in nodes:
				self.nodes[n].color = self.nodes[n].next_color()
				self.prune_colors(n, self.nodes[n].color)
				nodes.remove(self.nodes[n])

	def is_solved(self):
		for n in self.nodes:
			if self.nodes[n].color == -1:
				return False
		return True

	def is_feasible(self):	
		for c in self.color_classes:
			if self.color_classes[c].clashing_nodes > 0:
				return False
		return True	

	def populate_color_classes(self):
		for c in range(0, self.bound + 1 ):
			self.color_classes[c] = ColorClass()
		for n in self.nodes:
			node = self.nodes[n]
			color_class = self.color_classes[node.color]
			color_class.nodes.append(node.name)
			color_class.size += 1
		for cc in self.color_classes:
			for i in range(0, len(self.color_classes[cc].nodes)):
				for j in range(i+1, len(self.color_classes[cc].nodes)):
					if self.color_classes[cc].nodes[j] in self.nodes[self.color_classes[cc].nodes[i]].neighbors:
						self.color_classes[cc].clashing_nodes += 1	
		for c in self.color_classes:
			print c , " --> " , self.color_classes[c]					
		self.set_new_cost()			

	def randomly_initialize(self):
		for n in self.nodes:
			node = self.nodes[n]
			random_color = random.choice(range(0, self.bound))
			node.color = random_color
		self.populate_color_classes()	

	def set_new_cost(self):
		ct = 0
		cc = self.color_classes
		for c in cc:
			ct += cc[c].cost()
		self.current_cost = ct	

	def mutate(self, node, col):
		node = self.nodes[node.name]
		# old_node = copy.deepcopy(new_node)
		self.remove_color_sets(node)
		node.color = col
		self.add_color_sets(node)
		self.set_new_cost()
		# return old_node

	def remove_color_sets(self, node):
		self.color_classes[node.color].nodes.remove(node.name)	
		self.color_classes[node.color].size -= 1
		for r in node.neighbors:
			if r in self.color_classes[node.color].nodes:
				self.color_classes[node.color].clashing_nodes -= 1	

	def add_color_sets(self, node):
		self.color_classes[node.color].nodes.append(node.name)
		self.color_classes[node.color].size += 1
		for r in node.neighbors:
			if r in self.color_classes[node.color].nodes:
				self.color_classes[node.color].clashing_nodes += 1

	# def find_clashing(self, name, color):
	# 	cl = 0
	# 	for n in self.color_classes[color].nodes:
	# 		if n in self.nodes[name].neighbors:
	# 			cl += 1
	# 	return cl		




# generate a list of nodes which can be sorted by the number of each node's neighbors, or by the number of its available colors
def gen_nodes(graph):
	nodesBySize = []
	for x in graph.nodes:
		nodesBySize.append(graph.nodes[x])
	nodesBySize.sort(key=lambda x: len(x.neighbors))
	return nodesBySize

# the 'reset' function reassigns the maximum possible number of colors to each node in the graph
def reset(nodesBySize, graph, maxVal): 
	# in the beginning, all nodes have the same color set: the maximum allowed size is the highest degree in the graph
	if len(nodesBySize) > 0:
		maxDegree = len(nodesBySize[len(nodesBySize)-1].neighbors)
		mv = maxDegree if maxDegree < maxVal else maxVal
		graph.set_bound(mv+1)


# bubble sort works fast on semi-sorted lists
# every time a node is assigned a color value, that color has to be removed from its neighbors
# this changes a few nodes in the graph but not all nodes
# so if we were to keep a sorted list of nodes based on the number of available colors for each node,
# bubble sort would be a good candidate for re-sorting the list
def bubble_sort(alist):
    for passnum in range(len(alist)-1,0,-1):
        for i in range(passnum):
            if len(alist[i].color_vals)<len(alist[i+1].color_vals) or (len(alist[i].color_vals)==len(alist[i+1].color_vals) and len(alist[i].neighbors)>len(alist[i+1].neighbors)):
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp

# greedy search using a max neighbor/min color heuristic
def baseline(graph, nodes):
	while nodes:
		node = nodes.pop()
		if node.color == -1:
			col = graph.nodes[node.name].next_color()
			graph.nodes[node.name].color = col
			graph.prune_colors(node.name, node.color)
		bubble_sort(nodes)
	#print graph

# clique-based method
def clique_based(graph, nodes):
	while True:
		clique = graph.next_clique()
		if len(clique) <= 2:
			bubble_sort(nodes)
			baseline(graph, nodes)
			break
		graph.color_clique(clique, nodes)


def temperature(old_t, alpha):
	new_t = alpha * old_t
	return new_t

def iteration(old_alpha):
	new_alpha = old_alpha + ((1.0 - old_alpha) * 9 / 10)
	return new_alpha	

def hot(old_cost, new_cost, t):
	prob = math.exp(-(new_cost - old_cost)/t)
	return random.random() <= prob

def local_search(graph, current_bound):
	graph.bound = current_bound
	graph.populate_color_classes()
	#graph.randomly_initialize()
	min_graph = copy.deepcopy(graph)
	min_cost = graph.current_cost	
	alpha = 0.9
	t = 1.5
	i = 0
	while t > 0.2:
		print t
		i += 1
		old_cost = graph.current_cost
		random_node = random.choice(graph.nodes)
		old_color = random_node.color
		new_color = random.choice(range(0, graph.bound))

		graph.mutate(random_node, new_color)
		new_cost = graph.current_cost

		# print old_cost,'\t',new_cost

		if new_cost < old_cost:
			if new_cost < min_cost:
				min_cost = new_cost
				min_graph =  copy.deepcopy(graph)
		elif hot(old_cost, new_cost, t):
			print 'risking it'		
		else:
			graph.mutate(random_node, old_color)				
		alpha = iteration(alpha)
		t = temperature(t, alpha)
	print i		
	print min_graph.is_feasible()						
	return min_graph	



def solve_it(input_data):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')
	#print input_data
	# for l in lines:
	# 	print l
	first_line = lines[0].split()
	node_count = int(first_line[0])
	edge_count = int(first_line[1])

	graph = Graph(node_count, edge_count)
	edges = []
	for i in range(1, edge_count + 1):
		line = lines[i]
		parts = line.split()
		edges.append((int(parts[0]), int(parts[1])))
		source = Node(int(parts[0]))
		dest = Node(int(parts[1]))
		if source.name not in graph.nodes:
			graph.nodes[source.name] = source
		if dest.name not in graph.nodes:
			graph.nodes[dest.name] = dest
		graph.nodes[source.name].neighbors.append(dest.name)
		graph.nodes[source.name].ignore.append(False)
		graph.nodes[dest.name].neighbors.append(source.name)
		graph.nodes[dest.name].ignore.append(False)

	# in addition to the graph, generate a sorted list of nodes which you can keep track of by the number of neighbors or by the number of remaining color values
	nodesBySize = gen_nodes(graph)
	nodesBySizeBackUp = nodesBySize[:]
	reset(nodesBySize, graph, sys.maxint)	

	# run a clique-coloring algorithm to come up with an initial upper bound for the graph
	clique_based(graph, nodesBySize)

	# use the baseline algorithm to come up with a starting point
	graph = local_search(graph, graph.find_max_colors() - 1)
	# topDown(graph)


	# build a trivial solution
	# every node has its own color
	solution = []
	maxColor = 0
	for i in range(0, node_count):
		col = graph.nodes[i].color
		if col > maxColor:
			maxColor = col
		solution.append(col)

	# prepare the solution in the specified output format
	output_data = str(maxColor+1) + ' ' + str(0) + '\n'
	output_data += ' '.join(map(str, solution))

	return output_data


import sys

if __name__ == '__main__':
	if len(sys.argv) > 1:
		file_location = sys.argv[1].strip()
		input_data_file = open(file_location, 'r')
		input_data = ''.join(input_data_file.readlines())
		input_data_file.close()
		print solve_it(input_data)
	else:
		print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'

