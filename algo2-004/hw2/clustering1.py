#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from sets import Set

from collections import namedtuple
Edge = namedtuple("Edge", ['source', 'dest', 'distance'])


#node object
class Node:
	def __init__(self, nm):
		self.name = nm
		self.parent = self
		self.rank = 0
	def __str__(self):
		return str(self.name)
	def __repr__(self):
		return "Node(%s, %s)" % (self.name, self.parent.name)
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

#union-find data structure with path compression
# def MakeSet(x):
#      x.parent = x
#      x.rank   = 0

def Union(x, y):
     xRoot = Find(x)
     yRoot = Find(y)
     if xRoot.rank > yRoot.rank:
         yRoot.parent = xRoot
     elif xRoot.rank < yRoot.rank:
         xRoot.parent = yRoot
     elif xRoot != yRoot: # Unless x and y are already in same set, merge them
         yRoot.parent = xRoot
         xRoot.rank = xRoot.rank + 1

def Find(x):
     if x.parent == x:
        return x
     else:
        x.parent = Find(x.parent)
        return x.parent

def print_clusters(nodes):
	for node in nodes:
		print Find(node)

def find_crossing_edge(nodes, edges):
	for edge in edges:
		if Find(nodes[edge.source.name]) != Find(nodes[edge.dest.name]):
			return edge.distance		

def solve_it(input_data):
	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	node_count = int(firstLine[0])
	line_count = int(firstLine[1])

	edges = []
	nodes = {}
	for i in range(1, line_count+1):
		line = lines[i]
		parts = line.split()
		source = Node(int(parts[0]))
		dest = Node(int(parts[1]))
		dist = int(parts[2])
		edges.append(Edge(source, dest, dist))
		nodes[source.name] = (source)
		nodes[dest.name] = (dest)

	edges.sort(key=lambda x: x.distance, reverse = True)

	target = 4
	curr_clusters = node_count
	while curr_clusters > target:
		edge = edges.pop()
		if Find(nodes[edge.source.name]).name != Find(nodes[edge.dest.name]).name:
			Union(nodes[edge.source.name], nodes[edge.dest.name])
			curr_clusters -= 1
	return find_crossing_edge(nodes, reversed(edges))


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

