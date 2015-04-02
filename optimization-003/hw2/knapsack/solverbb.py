#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import sys
sys.setrecursionlimit(100000) # does this help?

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

#each node represents a node in the traversal tree
class Node:
	def __init__(self, index = -1, currvalue = 0, currcapacity = 0, estimate = 0):
		self.index = index
		self.currvalue = currvalue
		self.currcapacity = currcapacity
		self.estimate = estimate
		self.path = []
	def __str__(self):
		return "Node(index = {i}, currvalue = {cv}, currcapacity = {cc}, estimate = {e})".format(i = self.index, cv = self.currvalue, cc = self.currcapacity, e = self.estimate)

#parse the traversal tree using branch and bound (possibly with linear relaxation)
def parse(items, capacity, ideal, linear_relaxation):
	maxvalue = -sys.float_info.max
	root = Node()
	root.index = -1
	root.currvalue = 0
	root.currcapacity = capacity
	root.estimate = ideal
	stack = []
	stack.append(root)
	solution = []
	while stack:
		currnode = stack.pop()
		branching = False
		if len(currnode.path) == len(items):
			#print 'reached leaf, returning {m}'.format(m = max(currnode.currvalue, maxvalue))
			if currnode.currvalue > maxvalue:
				maxvalue = currnode.currvalue
				solution = currnode.path
			continue

		if len(currnode.path) == 0:
			print 'beginning...'
		else:
			print 'branching {dir} on node {n}'.format(dir = 'left' if currnode.path[len(currnode.path)-1] == 1 else 'right', n = items[currnode.index])
		print 'now analyzing currvalue {currvalue}, currcapacity {currcapacity},  estimate {currgoal}, and maxvalue {maxvalue}'.format(currvalue = currnode.currvalue, currcapacity = currnode.currcapacity, currgoal = currnode.estimate, maxvalue = maxvalue)
		#generate a node to inclue the current item
		leftNode = Node()
		leftNode.index = currnode.index + 1
		leftNode.currvalue = currnode.currvalue + items[leftNode.index].value
		leftNode.currcapacity = currnode.currcapacity - items[leftNode.index].weight
		leftNode.estimate = currnode.estimate
		leftNode.path = currnode.path + [1]
		#generate a node to exclude the current item
		rightNode = Node()
		rightNode.index = currnode.index + 1
		rightNode.currvalue = currnode.currvalue
		rightNode.currcapacity = currnode.currcapacity
		rightNode.estimate = getBound(items[rightNode.index + 1:], rightNode.currcapacity) if linear_relaxation else currnode.estimate - items[rightNode.index].value
		rightNode.path = currnode.path + [0]
	
		if rightNode.estimate + rightNode.currvalue >= maxvalue:
			branching = True
			stack.append(rightNode)
		if leftNode.currcapacity >= 0:
			branching = True
			stack.append(leftNode)

		if not branching:
			print 'cannot branch, returning {m}, unused capacity {c}'.format(m = max(currnode.currvalue, maxvalue), c = currnode.currcapacity)
			if currnode.currvalue > maxvalue:
				maxvalue = currnode.currvalue
				solution = currnode.path
	return (maxvalue, solution)


def getBound(items, capacity):
	currcap = 0
	goal = 0
	for i in items:
		if currcap + i.weight < capacity:
			goal = goal + i.value
			currcap = currcap + i.weight
		else:
			goal = goal + (((capacity - currcap) * i.value) / i.weight)
			break
	return goal

def solve_it(input_data):
	return solver(input_data, True)
def solver(input_data, linear_relaxation):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	item_count = int(firstLine[0])
	capacity = int(firstLine[1])

	items = []
	goal = 0

	for i in range(1, item_count+1):
		line = lines[i]
		parts = line.split()
		items.append(Item(i-1, int(parts[0]), int(parts[1])))
		#if not performing linear relaxation, set the estimate as the sum of all weights
		if not linear_relaxation:
			goal = goal + int(parts[0])

	#if performing linear relaxation, relax the integrality constraint to come up with a good bound
	if linear_relaxation:
		items.sort(key=lambda x: x.value/x.weight, reverse = True)
		goal = getBound(items, capacity)
	(value, path) = parse(items, capacity, goal, linear_relaxation)

	#performing linear relaxation changes the order of 'items', so the path variable needs to be reconstructed
	taken = [0]*len(items)
	if linear_relaxation:
		for i in range(len(path)):
			if path[i] == 1:
				taken[items[i].index] = 1
	else:
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

