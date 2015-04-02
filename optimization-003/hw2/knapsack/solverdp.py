#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    # value = 0
    # weight = 0
    # taken = [0]*len(items)

    # for item in items:
    #     if weight + item.weight <= capacity:
    #         taken[item.index] = 1
    #         value += item.value
    #         weight += item.weight

    valmatrix = [[0 for x in range(capacity+1)] for x in range(len(items))]

    for j in range(0, len(items)):
		for i in range(1, capacity+1):
			opt1 = valmatrix[j-1][i]
			opt2 = 0
			if items[j].weight <= i:
				opt2 = valmatrix[j-1][i-items[j].weight]+items[j].value
			if opt2 > opt1:
				valmatrix[j][i] = opt2
			else:
				valmatrix[j][i] = opt1


    i = capacity
    j = len(items)-1
    value = valmatrix[j][i]
    taken = [0]*len(items)
    while i>=0 and j>=0:
    	if j == 0 and valmatrix[j][i] > 0:
    		taken[j] = 1
    	if j > 0 and valmatrix[j-1][i] < valmatrix[j][i]:
    		taken[j] = 1
    		i =  i - items[j].weight
    	j = j-1
    
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

