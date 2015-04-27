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
		cost += edges[p[0]][p[1]].cost
	return cost 

def length(path, edges):
	cost = 0
	for p in path:
		cost += edges[p[0]][p[1]].dist
	return cost 	

def find_edge(edges, source, dest):
	return edges[source][dest]

# flag and penalize the edge in the current path with the highest utility
def flag_high_utility(path, edges, lmda):
	maxutil = -sys.maxint - 1
	maxutiledge = None
	for i in range(0, len(path)):
		p = path[i]
		e = edges[p[0]][p[1]]
		if e.utility() > maxutil:
			maxutil = e.utility()
			maxutiledge = i
	p = path[maxutiledge]		     
	edges[p[0]][p[1]].penalty += 1
	edges[p[0]][p[1]].cost += lmda
	edges[p[0]][p[1]].active = True
	return maxutiledge

# given a path and two edges to be swapped, determine whether swapping them would reduce the objective function
def viable(path, i, j, edges): 
	swap1 = path[i]
	swap2 = path[j]       
	# you can't swap two edges which have one endpoint in common
	if swap1[0] == swap2[0] or swap1[1] == swap2[1] or swap1[0] == swap2[1] == swap1[1] == swap2[0]:
		return False
	# find the endpoints to swap
	swapped1 = edges[swap1[0]][swap2[0]] if i < j else edges[swap2[1]][swap1[1]]
	swapped2 = edges[swap1[1]][swap2[1]] if i < j else edges[swap2[0]][swap1[0]]
	
	# find the new cost and compare it to the old cost
	discount = swapped1.cost + swapped2.cost - edges[swap1[0]][swap1[1]].cost - edges[swap2[0]][swap2[1]].cost
	return discount

def print_path(path):
	output = ''
	for p in path:
		output += str(p[0]) + ' --> ' + str(p[1]) + '|'
	return output       

# swap two edges in the current path
def swap(currpath, i, j, edges):
	# print print_path(currpath, edges)
	# print 'swapping edges ', edges[swap1], ' and ', edges[swap2]
	# find the right endpoints to swap
	swap1 = currpath[i]
	swap2 = currpath[j]
	firstedge = swap1 if i < j else swap2
	secondedge = swap2 if i < j else swap1
	firstedgeindex = i if i < j else j
	secondedgeindex = j if i < j else i
	currpath[firstedgeindex] = (firstedge[0], secondedge[0]) #find_edge(edges, edges[firstedge].source, edges[secondedge].source)
	for i in range(firstedgeindex + 1, secondedgeindex):
		currpath[i] = (currpath[i][1], currpath[i][0]) #find_edge(edges, edges[currpath[i]].dest, edges[currpath[i]].source)
	reverse(currpath, firstedgeindex + 1, secondedgeindex)  
	currpath[secondedgeindex] = (firstedge[1], secondedge[1]) #find_edge(edges, edges[firstedge].dest, edges[secondedge].dest) 

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
def parse(edges):
	minlength = sys.float_info.max
	minpath = None
	currpath = []
	# initialize path in order of cities
	for i in range(0, len(edges)):
		source = i
		dest = (i+1) % len(edges)
		currpath.append((source, dest))
		# for k in range(0, len(edges)): 
		# 	edge = edges[k]
		# 	if edge.source == cities[source].name and edge.dest == cities[dest].name:
		# 		currpath.append(k)  
	# for p in currpath:
	#   print edges[p].source, ' --> ', edges[p].dest               
	currcost = estimate(currpath, edges)   
	lmda =  currcost * 0.3 / len(edges)        
	iteration = 0   
	while iteration < 500000:
		iteration += 1  
		print iteration
		# activeedge = flag_high_utility(currpath, edges, lmda)
		while True:
			activeedge = flag_high_utility(currpath, edges, lmda)   
			bestswap = None
			mindisc = sys.maxint
			for swapcandidate in range(0, len(currpath)):
				if not edges[currpath[swapcandidate][0]][currpath[swapcandidate][1]].active:
					disc = viable(currpath, activeedge, swapcandidate, edges)
					if disc < 0 and disc < mindisc:
						mindisc = disc
						bestswap = swapcandidate	
			if bestswap is not None:			
				swap(currpath, activeedge, bestswap, edges)
				edges[currpath[activeedge][0]][currpath[activeedge][1]].active = False
				edges[currpath[bestswap][0]][currpath[bestswap][1]].active = True
			# if you're stuck in a local minimum, break out and go for another iteration	
			else:	
				edges[currpath[activeedge][0]][currpath[activeedge][1]].active = False
				break  
		currcost = estimate(currpath, edges)
		currlength = length(currpath, edges)
		if currlength < minlength:
			minlength = currlength
			minpath = currpath[:]
	print minpath						        
	return (minlength, minpath)             


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

	edges = [[0 for x in range(0, len(cities))] for y in range(0, len(cities))]
	for c1 in cities:
		for c2 in cities:
			if c1.name != c2.name:
				dist = distance(c1, c2)
				edge = Edge(c1.name, c2.name, dist)
				edges[c1.name][c2.name] = edge
			else:
				edge = Edge(c1.name, c2.name, 0)	
				edges[c1.name][c2.name] = edge

	del cities
	# edges.sort(key=lambda x: x.utility(), reverse=True) 

	(value, path) = parse(edges)

	taken = []
	for p in path:
		taken.append(p[0])
	# cost = 0
	# for i in range(0, len(taken) - 1):
	# 	source = taken[i]
	# 	dest = taken[(i + 1) % len(taken)]
	# 	dist = edges[find_edge(edges, source, dest)].dist
	# 	cost += dist
	# print cost	
	
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

