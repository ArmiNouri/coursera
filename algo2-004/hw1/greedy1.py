#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import sys
sys.setrecursionlimit(100000) # does this help?

from collections import namedtuple
Job = namedtuple("Job", ['weight', 'length', 'score'])


def solve_it(input_data):
	# Modify this code to run your optimization algorithm

	# parse the input
	lines = input_data.split('\n')

	firstLine = lines[0]
	job_count = int(firstLine)

	jobs = []

	for i in range(1, job_count+1):
		line = lines[i]
		parts = line.split()
		jobs.append(Job(int(parts[0]), int(parts[1]), int(parts[0])- int(parts[1])))

	jobs.sort(key=lambda x: (x.score, x.weight), reverse = True)

	weighted_sum = 0;
	current_time = 0
	for job in jobs:
		current_time = current_time + job.length
		weighted_sum = weighted_sum + job.weight * current_time
	
	return weighted_sum


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

