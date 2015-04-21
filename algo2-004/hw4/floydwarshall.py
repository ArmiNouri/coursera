#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from sets import Set

from collections import namedtuple


#node object
class Node:
	def __init__(self, nm):
		self.name = nm
		self.adjacent = {}
	def __str__(self):
		return 'Node ({n}) - neighbors: {a}'.format(n = str(self.name), a = self.adjacent)
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
	
	n = graph.node_count

	matrix = [[[0 for k in xrange(n)] for j in xrange(n)] for i in xrange(n)]
	nodes = []
	for n in graph.nodes:
		nodes.append(graph.nodes[n])

	# floyd_warshall

	#initialize
	for i in range(0, n):
		for j in range(0, n):
			print i,'\t',j,'\t',k
			source = nodes[i]
			dest = nodes[j]
			if source.name == dest.name:
				# this is technically unnecessary since the matrix is already initiated to zero 
				matrix[i][j][0] = 0
			elif dest.name in source.adjacent:
				matrix[i][j][0] = source.adjacent[dest.name]
			else:
				matrix[i][j][0] = sys.maxint	

	# propagate
	for k in range(1, n):
		for i in range(0, n):
			for j in range(0, n):
				print i,'\t',j,'\t',k
				source = nodes[i]
				dest = nodes[j]
				case_one = matrix[i][j][k-1]	
				case_two = matrix[i][k][k-1] + matrix[k][j][k-1]
				matrix[i][j][k] = case_one if case_one < case_two else case_two				

	# making sure there are no negative cycles
	for i in range(0, n):
		if matrix[i][i][n-1] < 0:
			return None 

	# finding the minimum path				
	min_path = sys.maxint
	for i in range(0, n):
		for j in range(0, n):
			if i != j and matrix[i][j][n-1] < min_path:
				min_path = matrix[i][j][n-1]
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

