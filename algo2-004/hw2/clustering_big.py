#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from sets import Set
import math
from collections import Counter

#read a line as the binary representation of a number
def read_as_binary(line, size):
	num = 0
	for i in range(0, size):
		num += int(line[i]) * math.pow(2, i)
	return int(num)

#count 1's in a given number's binary representation
def count_1s(num):
	return (bin(num)[2:]).count('1')

#node object
class Node:
	def __init__(self, nm):
		self.name = nm
		self.parent = self
		self.rank = 0
	def __str__(self):
		return str(self.name)
	def __repr__(self):
		return "Node(%s, %s)" % (self.name, self.parent)
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



def solve_it(input_data):

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0].split()
	node_count = int(firstLine[0])
	bit_count = int(firstLine[1])

	#build a dictionary of nodes where the key specifies how many 1s there are in the node's name
	nodeset = {}
	for i in range(0, bit_count):
		nodeset[i] = Set([])

	for i in range(1, node_count+1):
		line = lines[i].split()
		node = read_as_binary(line, bit_count)
		count_1 = line.count('1')
		nodeset[count_1].add(Node(node))

	#add all nodes to the union-find data structure
	# for i in nodeset:
	# 	[MakeSet(node) for node in nodeset[i]]

	min_spacing = 3
	num_clusters = node_count

	#for each set of nodes, look through the nodes with the same number of 1's, or one more or one less 1's, or two more or two less 1's.
	#these are the nodes whose distance from the current node can be 1 or 2
	#union those nodes into clusters
	for k in nodeset:
		print 'Now looking at nodes with ',k,' ones in them.'
		same_set = nodeset[k]
		one_more = nodeset[k+1] if k+1 < len(nodeset) else Set([])
		one_less = nodeset[k-1] if k-1 >= 0 else Set([])
		two_more = nodeset[k+2] if k+2 < len(nodeset) else Set([])
		two_less = nodeset[k-2] if k-2 >= 0 else Set([])
		for i in nodeset[k]:
			for j in same_set:
				if Find(i) != Find(j) and count_1s(i.name^j.name) < min_spacing:
					print 'Found nodes: ',i,' and ',j
					Union(i, j)
					num_clusters -= 1
			for j in one_more:
				if Find(i) != Find(j) and count_1s(i.name^j.name) < min_spacing:
					print 'Found nodes: ',i,' and ',j
					Union(i, j)
					num_clusters -= 1
			for j in one_less:
				if Find(i) != Find(j) and count_1s(i.name^j.name) < min_spacing:
					print 'Found nodes: ',i,' and ',j
					Union(i, j)
					num_clusters -= 1
			for j in two_more:
				if Find(i) != Find(j) and count_1s(i.name^j.name) < min_spacing:
					print 'Found nodes: ',i,' and ',j
					Union(i, j)
					num_clusters -= 1
			for j in two_less:
				if Find(i) != Find(j) and count_1s(i.name^j.name) < min_spacing:
					print 'Found nodes: ',i,' and ',j
					Union(i, j)
					num_clusters -= 1			
	return num_clusters

if __name__ == '__main__':
	if len(sys.argv) > 1:
		file_location = sys.argv[1].strip()
		input_data_file = open(file_location, 'r')
		input_data = ''.join(input_data_file.readlines())
		input_data_file.close()
		print solve_it(input_data)
	else:
		print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

