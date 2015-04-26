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


class City:
	def __init__(self, nm, xcoord, ycoord):
		self.name = nm
		self.x = xcoord
		self.y = ycoord

class Edge:
	def __init__(self, source, dest, dist):
		self.source = source
		self.dest = dest
		self.dist = dist
		self.cost = dist
		self.penalty = 0
		self.active = False

	def utility(self):
		return self.dist / (1 + self.penalty)

	def __str__(self):
		return 'Source: {s}, Destination: {d}, Distance: {i}, Cost: {c}, Utility: {u}'.format(s = self.source, d = self.dest, i = self.dist, c = self.cost, u = self.utility())	



def distance(c1, c2):
	return math.sqrt(math.pow(c1.x - c2.x, 2) + math.pow(c1.y - c2.y, 2))

def estimate(path, edges):
	cost = 0
	for p in path:
		cost += edges[p].dist
	return cost	

def find_edge(edges, source, dest):
	for i in range(0, len(edges)):
		e = edges[i]
		if e.source == source and e.dest == dest:
			return i

# flag and penalize the edge in the current path with the highest utility
def flag_high_utility(path, edges, lmda):
	maxutil = -sys.maxint - 1
	maxutiledge = -1
	for p in path:
		e = edges[p]
		if e.utility() > maxutil:
			maxutil = e.utility()
			maxutiledge = p		
	edges[maxutiledge].penalty += 1
	edges[maxutiledge].cost += lmda
	edges[maxutiledge].active = True
	return maxutiledge

# given a path and two edges to be swapped, determine whether swapping them would reduce the objective function
def viable(path, swap1, swap2, currcost, edges):		
	# you can't swap two edges which have one endpoint in common
	if edges[swap1].source == edges[swap2].source or edges[swap1].dest == edges[swap2].source or edges[swap1].dest == edges[swap2].dest or edges[swap1].source == edges[swap2].dest:
		return False
	# find the right endpoints to swap
	swapped1 = find_edge(edges, edges[swap1].source, edges[swap2].source) if path.index(swap1) < path.index(swap2) else find_edge(edges, edges[swap2].dest, edges[swap1].dest)
	swapped2 = find_edge(edges, edges[swap1].dest, edges[swap2].dest) if path.index(swap1) < path.index(swap2) else find_edge(edges, edges[swap2].source, edges[swap1].source)	
	
	# find the new cost and compare it to the old cost
	newcost = currcost - edges[swap1].cost - edges[swap2].cost + edges[swapped1].cost + edges[swapped2].cost
	return True if newcost < currcost else False

def print_path(path, edges):
	output = ''
	for p in path:
		output += str(edges[p].source) + ' --> ' + str(edges[p].dest) + '|'
	return output		

# swap two edges in the current path
def swap(currpath, swap1, swap2, edges):
	# print print_path(currpath, edges)
	# print 'swapping edges ', edges[swap1], ' and ', edges[swap2]
	# find the right endpoints to swap
	firstedge = swap1 if currpath.index(swap1) < currpath.index(swap2) else swap2
	secondedge = swap2 if currpath.index(swap1) < currpath.index(swap2) else swap1
	firstedgeindex = currpath.index(firstedge)
	secondedgeindex = currpath.index(secondedge)
	currpath[firstedgeindex] = find_edge(edges, edges[firstedge].source, edges[secondedge].source)
	for i in range(firstedgeindex + 1, secondedgeindex):
		currpath[i] = find_edge(edges, edges[currpath[i]].dest, edges[currpath[i]].source)
	reverse(currpath, firstedgeindex + 1, secondedgeindex)	
	currpath[secondedgeindex] = find_edge(edges, edges[firstedge].dest, edges[secondedge].dest)	

def reverse(path, beginning, end):
	i = beginning
	j = end - 1
	while i < j:
		temp = path[i]
		path[i] = path[j]
		path[j] = temp
		i +=1
		j -= 1	

#parse the traversal tree using guided local search
def parse(edges, cities):
	mincost = sys.float_info.max
	minpath = None
	currpath = []
	for i in range(0, len(cities)):
		source = i
		dest = (i+1) % len(cities)
		for k in range(0, len(edges)): 
			edge = edges[k]
			if edge.source == cities[source].name and edge.dest == cities[dest].name:
				currpath.append(k)	
	# for p in currpath:
	# 	print edges[p].source, ' --> ', edges[p].dest				
	currcost = estimate(currpath, edges)	
	lmda =  currcost * 0.3 / len(cities)		
	iteration = 0	
	while iteration < 200000:
		iteration += 1	
		print iteration
		# activeedge = flag_high_utility(currpath, edges, lmda)
		while True:
			activeedge = flag_high_utility(currpath, edges, lmda)	
			found = False
			for inactiveedge in currpath:
				# print '\n'
				if not edges[inactiveedge].active and viable(currpath, activeedge, inactiveedge, currcost, edges):
					# print print_path(currpath, edges)
					# print currpath.index(activeedge),'\t',currpath.index(inactiveedge)
					swap(currpath, activeedge, inactiveedge, edges)
					# print '\n'
					edges[activeedge].active = False
					found = True
					break
			if not found:
				break	
			
		currcost = estimate(currpath, edges)
		if currcost < mincost:
			mincost = currcost
			minpath = currpath

	tour = []
	edge = None
	for i in minpath:
		edge = edges[i]
		tour.append(edge.source)
	tour.append(edge.dest)

	# for p in minpath:
	# 	print edges[p].source, ' --> ', edges[p].dest	

	return 	(mincost, tour)				


def solve_it(input_data):
	return solver(input_data, True)
def solver(input_data, linear_relaxation):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	city_count = int(firstLine[0])

	cities = []
	for i in range(1, city_count+1):
		line = lines[i]
		parts = line.split()
		city = City(i-1, float(parts[0]), float(parts[1]))
		cities.append(city)

	# # each city has a distance to each other city
	# for c1 in cities:
	# 	for c2 in cities:
	# 		if c1 != c2:
	# 			city1 = cities[c1]
	# 			city2 = cities[c2]
	# 			dist = distance(city1, city2)
	# 			n2 = Neighbor(city2.name, dist)
	# 			city1.neighbors.append(n2)

	# # sort each cities neighbors by their distance from it
	# for c in cities:
	# 	city = cities[c]
	# 	city.neighbors.sort(key = lambda x: x.distance)

	edges = []
	for c1 in cities:
		for c2 in cities:
			if c1.name != c2.name:
				dist = distance(c1, c2)
				edge = Edge(c1.name, c2.name, dist)
				edges.append(edge)

	edges.sort(key=lambda x: x.utility(), reverse=True)	

	(value, path) = parse(edges, cities)

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

