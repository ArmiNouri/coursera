#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import sys
sys.setrecursionlimit(100000) # does this help?
import math
from sets import Set
import random

from collections import namedtuple
Neighbor = namedtuple("Neighbor", ['name', 'distance'])

#each node represents a node in the traversal tree
class Node:
	def __init__(self, ind = -1, currvalue = 0, estimate = 0):
		self.index = ind
		self.currvalue = currvalue
		self.estimate = estimate
		self.path = []
	def __str__(self):
		return "Node(index = {i}, currvalue = {cv}, estimate = {e})".format(i = self.index, cv = self.currvalue, e = self.estimate)

class City:
	def __init__(self, nm, xcoord, ycoord):
		self.name = nm
		self.x = xcoord
		self.y = ycoord
		self.neighbors = []
	def get_close_neighbors(self, currnode, cities):
		ns = []
		i = 0
		for n in self.neighbors:
			if i > 2:
				break
			i+=1	
			if n.name in currnode.path:
				ns.append(cities[n.name])
		return ns		

def distance(c1, c2):
	return math.sqrt(math.pow(c1.x - c2.x, 2) + math.pow(c1.y - c2.y, 2))

def get_estimate(currnode, cities):
	estimate = 0
	for c in cities:
		if c not in currnode.path:
			node = cities[c]
			for n in node.get_close_neighbors(currnode, cities):
				neighbor = cities[n.name]
				estimate += distance(node, neighbor)
	return estimate / 2	

#parse the traversal tree using branch and bound
def parse(cities):
	minvalue = sys.float_info.max
	root = Node()
	root.index = -1
	root.currvalue = 0
	# begin from a random city
	begin = random.choice(cities).name
	root.path.append(begin)
	root.estimate = get_estimate(root, cities)
	stack = []
	stack.append(root)
	solution = []
	while stack:
		currnode = stack.pop()
		# once you've found a full tour, inspect it to determine whether it improves on the current solution
		if len(currnode.path) == len(cities):
			#print 'reached leaf, returning {m}'.format(m = max(currnode.currvalue, maxvalue))
			if currnode.currvalue < minvalue:
				minvalue = currnode.currvalue
				solution = currnode.path
			continue

		if len(currnode.path) == 1:
			print 'beginning...'
		else:
			print 'branching on city {c}'.format(c = cities[currnode.path[-1]].name)
		print 'now analyzing currvalue {currvalue}, estimate {currgoal}, and minvalue {minvalue}'.format(currvalue = currnode.currvalue, currgoal = currnode.estimate, minvalue = minvalue)
		#generate a node to inspect each other city we can go to from here
		for neighbor in cities[currnode.path[-1]].neighbors:
			# the tour has to visit each neighbor exactly once
			# so ignore neghibors which have already been visited on the current path
			if neighbor.name not in currnode.path:
				print currnode.path
				i += 1
				next_node = Node()
				next_node.index = currnode.index + 1
				next_node.currvalue = currnode.currvalue + neighbor.distance
				next_node.path = currnode.path + [neighbor.name]
				next_node.estimate = get_estimate(next_node, cities)
				if next_node.estimate + next_node.currvalue < minvalue:
					stack.append(next_node)
				else:
					print 'ignoring current branch...'
	return (minvalue, solution)


def solve_it(input_data):
	return solver(input_data, True)
def solver(input_data, linear_relaxation):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	city_count = int(firstLine[0])

	cities = {}
	for i in range(1, city_count+1):
		line = lines[i]
		parts = line.split()
		city = City(i-1, float(parts[0]), float(parts[1]))
		cities[city.name] = city

	# each city has a distance to each other city
	for c1 in cities:
		for c2 in cities:
			if c1 != c2:
				city1 = cities[c1]
				city2 = cities[c2]
				dist = distance(city1, city2)
				n2 = Neighbor(city2.name, dist)
				city1.neighbors.append(n2)

	# sort each cities neighbors by their distance from it
	for c in cities:
		city = cities[c]
		city.neighbors.sort(key = lambda x: x.distance)

	(value, path) = parse(cities)

	taken = path
	
	# prepare the solution in the specified output format
	output_data = str(value) + ' ' + str(0) + '\n'
	output_data += ' '.join(map(str, taken))
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
		print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

