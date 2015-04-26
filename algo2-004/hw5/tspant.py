#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import sys
sys.setrecursionlimit(100000) # does this help?
import math
from sets import Set
import random
from threading import Lock, Condition
from threading import *

from collections import namedtuple
Neighbor = namedtuple("Neighbor", ['name', 'distance'])

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

class Cities:
	def __init__(self, delta_mat, num_cities, tau_mat=None):
		self.len = num_cities
		self.delta_mat = delta_mat
		self.lock = Lock()

		# tau mat contains the amount of phermone at node x,y
		if tau_mat is None:
			self.tau_mat = []
			for i in range(0, self.len):
				self.tau_mat.append([0]*num_cities)

	def delta(self, r, s):
		return self.delta_mat[r][s]

	def tau(self, r, s):
		return self.tau_mat[r][s]

	# 1 / delta = eta or etha 
	def etha(self, r, s):
		return 1.0 / self.delta(r, s)

	# inner locks most likely not necessary
	def update_tau(self, r, s, val):
		lock = Lock()
		lock.acquire()
		self.tau_mat[r][s] = val
		lock.release()

	def reset_tau(self):
		lock = Lock()
		lock.acquire()
		avg = self.average_delta()

		# initial tau 
		self.tau0 = 1.0 / (self.len * 0.5 * avg)

		# print "Average = %s" % (avg,)
		# print "Tau0 = %s" % (self.tau0)

		for r in range(0, self.len):
			for s in range(0, self.len):
				self.tau_mat[r][s] = self.tau0
		lock.release()

	# average delta in delta matrix
	def average_delta(self):
		return self.average(self.delta_mat)

	# average tau in tau matrix
	def average_tau(self):
		return self.average(self.tau_mat)

	# average val of a matrix
	def average(self, matrix):
		sum = 0
		for r in range(0, self.len):
			for s in range(0, self.len):
				sum += matrix[r][s]

		avg = sum / (self.len * self.len)
		return avg	


class Ant(Thread):
	def __init__(self, ID, start_node, colony):
		Thread.__init__(self)
		self.ID = ID
		self.start_node = start_node
		self.colony = colony

		self.curr_node = self.start_node
		self.cities = self.colony.cities
		self.tour = []
		self.tour.append(self.start_node)
		self.path_cost = 0

		# same meaning as in standard equations
		self.Beta = 1
		#self.Q0 = 1  # Q0 = 1 works just fine for 10 city case (no explore)
		self.Q0 = 0.5
		self.Rho = 0.99

		# store the nodes remaining to be explored here
		self.nodes_to_visit = {}

		for i in range(0, self.cities.len):
			if i != self.start_node:
				self.nodes_to_visit[i] = i

		# create n X n matrix 0'd out to start
		self.tour_mat = []

		for i in range(0, self.cities.len):
			self.tour_mat.append([0]*self.cities.len)

	# overide Thread's run()
	def start(self):
		cities = self.colony.cities
		while not self.end():
			# we need exclusive access to the graph
			cities.lock.acquire()
			new_node = self.state_transition_rule(self.curr_node)
			self.path_cost += cities.delta(self.curr_node, new_node)

			self.tour.append(new_node)
			self.tour_mat[self.curr_node][new_node] = 1  #adjacency matrix representing path

			print "Ant %s : %s, %s" % (self.ID, self.tour, self.path_cost,)
			
			self.local_updating_rule(self.curr_node, new_node)
			cities.lock.release()

			self.curr_node = new_node

		# don't forget to close the tour
		self.path_cost += cities.delta(self.tour[-1], self.tour[0])

		# send our results to the colony
		self.colony.update(self)
		# print "Ant thread %s terminating." % (self.ID,)

		# allows thread to be restarted (calls Thread.__init__)
		self.__init__(self.ID, self.start_node, self.colony)

	def end(self):
		return not self.nodes_to_visit 

	# described in report -- determines next node to visit after curr_node
	def state_transition_rule(self, curr_node):
		cities = self.colony.cities
		q = random.random()
		max_node = -1

		if q < self.Q0:
			# print "Exploitation"
			max_val = -1
			val = None

			for node in self.nodes_to_visit.values():
				if cities.tau(curr_node, node) == 0:
					raise Exception("tau = 0")

				val = cities.tau(curr_node, node) * math.pow(cities.etha(curr_node, node), self.Beta)
				if val > max_val:
					max_val = val
					max_node = node
		else:
			# print "Exploration"
			sum = 0
			node = -1

			for node in self.nodes_to_visit.values():
				if cities.tau(curr_node, node) == 0:
					raise Exception("tau = 0")
				sum += cities.tau(curr_node, node) * math.pow(cities.etha(curr_node, node), self.Beta)
			if sum == 0:
				raise Exception("sum = 0")

			avg = sum / len(self.nodes_to_visit)

			# print "avg = %s" % (avg,)

			for node in self.nodes_to_visit.values():
				p = cities.tau(curr_node, node) * math.pow(cities.etha(curr_node, node), self.Beta) 
				if p > avg:
					# print "p = %s" % (p,)
					max_node = node

			if max_node == -1:
				max_node = node
		
		if max_node < 0:
			raise Exception("max_node < 0")

		del self.nodes_to_visit[max_node]
		
		return max_node

	# phermone update rule for indiv ants
	def local_updating_rule(self, curr_node, next_node):
		cities = self.colony.cities
		val = (1 - self.Rho) * cities.tau(curr_node, next_node) + (self.Rho * cities.tau0)
		cities.update_tau(curr_node, next_node, val)		  

class Colony:
	def __init__(self, cities, num_ants, num_iter):
		self.cities = cities
		self.num_ants = num_ants
		self.max_iter = num_iter
		self.Alpha = 0.1
		self.cond = Condition()
		self.reset()


	def reset(self):
		self.best_cost = sys.maxint
		self.best_tour = None
		self.best_tour_mat  = None
		self.last_best_path_iter = 0

	def start(self):
		self.ants = self.create_ants()
		self.curr_iter = 0

		while (self.curr_iter < self.max_iter):
			self.iterate()
			self.cond.acquire()
			# self.cond.wait()
			lock = self.cities.lock
			lock.acquire()
			self.global_updating_rule()
			lock.release()
			self.cond.release()

	def iterate(self):
		self.curr_cost = 0
		self.curr_ant = 0
		self.curr_iter += 1   
		for ant in self.ants:
			# print "starting ant = %s" % (ant.ID)
			ant.start()
			# print "ending ant = %s" % (ant.ID)

	def update(self, ant):
		lock = Lock()
		lock.acquire()

		self.curr_ant += 1
		self.curr_cost += ant.path_cost	

		if ant.path_cost < self.best_cost:
			self.best_cost = ant.path_cost
			self.best_tour = ant.tour
			self.best_tour_mat = ant.tour_mat
			self.last_best_path_iteration = self.curr_iter

		if self.curr_ant == len(self.ants):
			self.curr_cost /= len(self.ants)
			self.cond.acquire()
			self.cond.notify()
			self.cond.release()

		lock.release()

	def create_ants(self):
		self.reset()
		ants = []
		for i in range(0, self.num_ants):
			ant = Ant(i, random.randint(0, self.cities.len-1), self)
			ants.append(ant)
		return ants
	
	def global_updating_rule(self):
		evap = 0
		depos = 0

		for r in range(0, self.cities.len):
			for s in range(0, self.cities.len):
				if r != s:
					delt_tau = self.best_tour_mat[r][s] / self.best_cost
					evaporation = (1 - self.Alpha) * self.cities.tau(r, s)
					deposition = self.Alpha * delt_tau
					self.cities.update_tau(r, s, evaporation + deposition)		


def distance(c1, c2):
	return math.sqrt(math.pow(c1.x - c2.x, 2) + math.pow(c1.y - c2.y, 2))

def parse(cs):
	# parameters for the ant colony
	num_ants = 50
	num_iter = 30
	num_repeat = 10

	delta_mat = [[0 for x in range(0, len(cs))] for y in range(0, len(cs))]
	for i in range(0, len(cs)):
		for j in range(0, len(cs)):
			delta_mat[i][j] = distance(cs[i], cs[j])

	cities = Cities(delta_mat, len(cs))
	best_tour = None
	best_cost = sys.maxint
	for i in range(0, num_repeat):
		cities.reset_tau()
		colony = Colony(cities, num_ants, num_iter)
		colony.start()
		if colony.best_cost < best_cost:
			best_tour = colony.best_tour
			best_cost = colony.best_cost
		print 'colony done'
	return (best_cost, best_tour)


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

if __name__ == '__main__':
	if len(sys.argv) > 1:
		file_location = sys.argv[1].strip()
		input_data_file = open(file_location, 'r')
		input_data = ''.join(input_data_file.readlines())
		input_data_file.close()
		print solve_it(input_data)
	else:
		print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

