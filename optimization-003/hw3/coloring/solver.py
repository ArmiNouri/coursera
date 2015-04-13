#!/usr/bin/python
# -*- coding: utf-8 -*-
from sets import Set
import copy

#define nodes in the graph
class Node:
	def __init__(self, name):
		self.name = name
		self.neighbors = []
		# this array flags all previsouly discovered cliques so they can be ignored in each new iteration
		self.ignore = []
		self.color = -1
		# this array holds available colors for the node
		self.colorVals = []
		# this field is used to keep track of paths when traversing the search tree; it facilitates backtracking
		self.parent = 0

	def __str__(self):
		out = ""
		for n in self.neighbors:
			out = out + str(n.name)+ ","
		return "Node(name = {n}, color = {c}, color_range = {r})'s neighbors:".format(n = self.name, c = self.color, r = self.colorVals)+"\n"+out+"\n"

	# choose the next available value in your color set
	def nextColor(self):
		if len(self.colorVals) > 0:
			col = self.colorVals[0]
			self.colorVals = self.colorVals[1:]
			return col
		else:
			return -1

	# remove a color value from your set of colors
	def pruneColor(self, col):
		if col in self.colorVals:
			self.colorVals.remove(col)

#define graph as a dictionary of nodes
class Graph:
	def __init__(self, nc, ec):
		self.nodes = {}
		self.node_count = nc
		self.edge_count = ec
		# initially, the lower bound on the chromatic number of the graph is set to zero
		# later, the largest clique found in the graph will repalce this value
		self.bound = 0

	def __str__(self):
		out = ""
		for nodeName in self.nodes:
			out = out + self.nodes[nodeName].__str__()
		return "Graph(node_count = {nc}, edge_count = {ec}) has these nodes:".format(nc = self.node_count, ec = self.edge_count)+"\n"+out
		
	def setBound(self, bound):
		self.bound = bound
		for n in self.nodes:
			self.nodes[n].colorVals = list(range(0, self.bound))
			self.nodes[n].color = -1
			self.nodes[n].ignore = [False] * len(self.nodes[n].neighbors)

	def findMaxColors(self):
		maxCols = 0
		for n in self.nodes:
			if self.nodes[n].color > maxCols:
				maxCols = self.nodes[n].color
		return maxCols + 1

	# given a recently colored node, remove its color from the set of legitimate colors from all of its neighbors
	def pruneColors(self, nodeName, nodeColor):
		for n in self.nodes[nodeName].neighbors:
			n.pruneColor(nodeColor)
			self.nodes[n.name].pruneColor(nodeColor)

	# pivot-based Bron-Kerbosch algorithm for finding cliques in the graph
	def BronKerbosch(self, R, P, X):
		if len(P) == 0 and len(X) == 0:
			# once you find a clique, mark its edges as 'ignored' so you don't double-count it next time
			for n in self.nodes:
				if self.nodes[n].name in R:
					for i in range(0, len(self.nodes[n].neighbors)):
						if self.nodes[n].neighbors[i].name in R:
							self.nodes[n].ignore[i] = True
			return R
		#choose a pivot vertex u in P ⋃ X
		u = P.union(X).pop()
		Nu = Set([])
		for i in range(0, len(self.nodes[u].neighbors)):
			if not self.nodes[u].ignore[i]:
				Nu.add(self.nodes[u].neighbors[i].name)
		for v in  P - Nu:
			Sv = Set([v])
			Nv = Set([])
			for i in range(0, len(self.nodes[v].neighbors)):
				if not self.nodes[v].ignore[i]:
					Nv.add(self.nodes[v].neighbors[i].name)
			return self.BronKerbosch(R.union(Sv), P.intersection(Nv), X.intersection(Nv))
			P = P - Sv
			X = X.union(Sv)

	# find a max clique in the graph using Bron-Kerbosch's algorithm
	def nextClique(self):
		R = Set([])
		P = Set([])
		X = Set([])
		for n in self.nodes:
			P.add(self.nodes[n].name)
		clique = self.BronKerbosch(R, P, X)
		return clique

	# given a clique, color it with varying colors
	def colorClique(self, clique, nodes):
		for n in clique:
			if self.nodes[n] in nodes:
				self.nodes[n].color = self.nodes[n].nextColor()
				self.pruneColors(n, self.nodes[n].color)
				nodes.remove(self.nodes[n])

	def isSolved(self):
		for n in self.nodes:
			if self.nodes[n].color == -1:
				return False
		return True


# generate a list of nodes which can be sorted by the number of each node's neighbors, or by the number of its available colors
def genNodes(graph):
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
		graph.setBound(mv+1)


# bubble sort works fast on semi-sorted lists
# every time a node is assigned a color value, that color has to be removed from its neighbors
# this changes a few nodes in the graph but not all nodes
# so if we were to keep a sorted list of nodes based on the number of available colors for each node,
# bubble sort would be a good candidate for re-sorting the list
def bubbleSort(alist):
    for passnum in range(len(alist)-1,0,-1):
        for i in range(passnum):
            if len(alist[i].colorVals)<len(alist[i+1].colorVals) or (len(alist[i].colorVals)==len(alist[i+1].colorVals) and len(alist[i].neighbors)>len(alist[i+1].neighbors)):
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp

# greedy search using a max neighbor/min color heuristic
def baseline(graph, nodes):
	while nodes:
		node = nodes.pop()
		if node.color == -1:
			col = graph.nodes[node.name].nextColor()
			graph.nodes[node.name].color = col
			graph.pruneColors(node.name, node.color)
		bubbleSort(nodes)
	#print graph

# clique-based method
def cliqueBased(graph, nodes):
	while True:
		clique = graph.nextClique()
		if len(clique) <= 2:
			bubbleSort(nodes)
			baseline(graph, nodes)
			break
		graph.colorClique(clique, nodes)

# bound-setter for the main method
def boundSetter(graph, nodes):
	while True:
		clique = graph.nextClique()
		if len(clique) <= 2:
			break
		graph.colorClique(clique, nodes)
		bubbleSort(nodes)

# the algorithm uses a clique-based parsing method to calculate a lower-bound and upper-bound for the graph's chromatic number
# 	- lower-bound: size of the largest clique in the graph
#	- upper-bound: size of the highest degree in the graph
# then, beginning from the lower-bound, the algorithm traverses the search tree to find a proper coloring for the graph
# whenever it runs out of options, it adds one color to the lower bound
# whenever it exceeds the upper bound, it backtracks
def search(graph, nodes, bound):
	print 'trying to find an optimal solution for bound = ',bound - 1
	# back up the curren graph and the current stack of nodes, so if the current run doesn't work, you can return the backups as the optimal answer
	graphBackUp = copy.deepcopy(graph)
	nodesBackUp = nodes[:]
	# decrement the bound and try to find a coloring
	graph.setBound(bound - 1)
	boundSetter(graph, nodes)
	while nodes:
		# each node's 'parent' flag tells us which level it's currently in; to save time, we won't backtrack more than a constant number of levels
		# this means the last proper coloring you found is the best coloring available within the bounds of the algorithm
		currNode = nodes.pop()
		if currNode.parent > graph.node_count:
			break
		# if you have any options left for the current node...
		if len(currNode.colorVals) > 0:
			# paint it with the next available color
			currNode.color = currNode.nextColor()
			# prune the colors from its neighbors
			graph.pruneColors(currNode.name, currNode.color)
			# set the parent of all remaining nodes to the current node, so you can backtrack later
			currNode.parent -= 1
			# re-order the remaining nodes so the ones with the fewest options are on top
			bubbleSort(nodes)
		#backtracking; reinsert node at the end of the stack and without changing the order, pick another node to color
		else:
			# if you've run out of options for the current node, increment it's 'level-indicator' and put it back in the queue
			currNode.parent += 1
			nodes.insert(0, currNode)
	# if the current round succeeded in finding a proper coloring, try a new round with a smaller bound
	if graph.isSolved():
		search(graph, nodesBackUp, graph.bound)
	else:
		return graphBackUp



def solve_it(input_data):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')
	#print input_data

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
		graph.nodes[source.name].neighbors.append(dest)
		graph.nodes[source.name].ignore.append(False)
		graph.nodes[dest.name].neighbors.append(source)
		graph.nodes[dest.name].ignore.append(False)

	# in addition to the graph, generate a sorted list of nodes which you can keep track of by the number of neighbors or by the number of remaining color values
	nodesBySize = genNodes(graph)
	nodesBySizeBackUp = nodesBySize[:]
	reset(nodesBySize, graph, sys.maxint)	

	# run a clique-coloring algorithm to come up with an initial upper bound for the graph
	cliqueBased(graph, nodesBySize)
	# use the baseline algorithm to come up with a starting point
	graph = search(graph, nodesBySizeBackUp, graph.findMaxColors())

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

