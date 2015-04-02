#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
from sets import Set

Edge = namedtuple("Edge", ['source', 'dest', 'weight']) 


def solve_it(input_data):
	#Parse the input
	lines = input_data.split('\n')

	first_line = lines[0].split()
	node_count = int(first_line[0])
	edge_count = int(first_line[1])

	edges = []
	unvisited = Set([])
	for i in range(1, edge_count+1):
		line = lines[i]
		parts = line.split()
		source = int(parts[0])
		dest = int(parts[1])
		weight = int(parts[2])
		unvisited.add(source)
		unvisited.add(dest)
		#Store each edge on twice, once indexed by source and once indexed by destination. This uses twice as much memory but allows a one-time sort 
		edges.append(Edge(source, dest, weight))
		edges.append(Edge(dest, source, weight))

	#Sort the edges by weight. Each edge is once sorted by its source, and once by its destination.
	edges.sort(key=lambda x: x.weight)

	mst = 0
	visited = Set([])
	node = unvisited.pop()
	visited.add(node)
	while len(visited) < node_count:
		found = False
		for edge in edges:
			#Since 'edges' is already sorted by weight, the first matching edge is bound to be the smallest edge that crosses the visited-unvisited cut
			if edge.source in visited and edge.dest in unvisited:
				print 'adding edge ',edge.source,'-->',edge.dest,'to tree'
				unvisited.remove(edge.dest)
				visited.add(edge.dest)
				mindEdge = edge.weight
				mst = mst + mindEdge
				found = True
				break
		#If you don't find any edges between visited and unvisited nodes, this means the graph is not connected.		
		if not found:
			exit(1)
	return mst


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

