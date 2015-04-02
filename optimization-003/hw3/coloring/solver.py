#!/usr/bin/python
# -*- coding: utf-8 -*-

#define nodes in the graph
class Node:
	def __init__(self, name):
		self.name = name
		self.neighbors = []
		self.color = -1
		#self.colorVals = list(range(0, maxColorVal))
		self.colorVals = []

	def __str__(self):
		out = ""
		for n in self.neighbors:
			out = out + str(n.name)+ ","
		return "Node(name = {n}, color = {c})'s neighbors:".format(n = self.name, c = self.color)+"\n"+out+"\n"

	def nextColor(self):
		if len(self.colorVals) > 0:
			col = self.colorVals[0]
			self.colorVals = self.colorVals[1:]
			return col
		else:
			return -1

	def pruneColor(self, col):
		if col in self.colorVals:
			self.colorVals.remove(col)


class Graph:
	def __init__(self, nc, ec):
		self.nodes = {}
		self.node_count = nc
		self.edge_count = ec
		# self.node_with_max_neighbors = -1

	def __str__(self):
		out = ""
		for nodeName in self.nodes:
			out = out + self.nodes[nodeName].__str__()
		return "Graph(node_count = {nc}, edge_count = {ec}) has these nodes:".format(nc = self.node_count, ec = self.edge_count)+"\n"+out

	def pruneColors(self, nodeName, nodeColor):
		for n in self.nodes[nodeName].neighbors:
			n.pruneColor(nodeColor)
			self.nodes[n.name].pruneColor(nodeColor)

def parse(graph, nodes):
	while nodes:
		node = nodes.pop()
		if node.color == -1:
			col = graph.nodes[node.name].nextColor()
			graph.nodes[node.name].color = col
			graph.pruneColors(node.name, node.color)
		nodes.sort(key=lambda x: (len(x.neighbors), -1*len(x.colorVals)))
	#print graph


def solve_it(input_data):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

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
		graph.nodes[dest.name].neighbors.append(source)

	nodesBySize = []
	for x in graph.nodes:
		nodesBySize.append(graph.nodes[x])
	nodesBySize.sort(key=lambda x: len(x.neighbors)) 
	if len(nodesBySize) > 0:
		mv = len(nodesBySize[len(nodesBySize)-1].neighbors)
		for n in graph.nodes:
			graph.nodes[n].colorVals = list(range(mv))

	parse(graph, nodesBySize)

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

