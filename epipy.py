from random import seed, randint, random, gauss, choice
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


class Person:
	def __init__(self, cell):
		self.status = "D"
		self.cell = cell
		self.change_date = 0

	def __str__(self):
		return str(self.cell) + " " + self.status + " " + str(self.change_date)


class Cell:
	def __init__(self, start, stop):
		self.status = "D"
		self.start = start
		self.stop = stop
		self.change_date = 0
		self.size = stop - start + 1

	def __str__(self):
		return self.status + " " + str(self.start) + " " + str(self.stop)


def normalize_array(array):		#Normira array
	sum_a = sum(array)
	for k in range(len(array)):
		array[k] = array[k]/sum_a
	return array


def calculate_grid_stats(people, states, N):	#Vrne normirano statistiko tistega dne
	stat = [0,0,0,0,0]
	for k in range(N):
		for j in range(len(states)):
			if people[k].status == states[j]:
				stat[j] += 1
	return normalize_array(stat)


def outcome(probability):	#Takšna verjetnost da vrne True
	if probability > 1:
		print("ERROR probability more than 1")
	else:
		seed(datetime.now())
		if (random() < probability):
			return True
		else:
			return False


def check_all_for_type(cell, i, people, type):	#Če so vsi člani celice istega tipa je takšen tudi tip celice
	for k in range(cell.start, cell.stop+1):
		if (people[k].status != type):
			return
	cell.status = type
	cell.change_date = i
	return


def check_if_any_K(cell, i, people):		#  Dc -> Kc,  D -> K
	for k in range(cell.start, cell.stop+1):
		if (people[k].status == "K"):
			cell.status = "K"
			cell.change_date = i
			for j in range(cell.start, cell.stop+1):
				if (j != k and people[j].status == "D"):
					people[j].status = "K"
					people[j].change_date = i+1
			return
	return


def check_if_any_B(cell, i, people):		#  Dc -> Kc,  D -> Ki
	for k in range(cell.start, cell.stop+1):
		if (people[k].status == "B"):
			cell.status = "B"
			cell.change_date = i
			for j in range(cell.start, cell.stop+1):
				if (j != k and people[j].status != "O"):
					people[j].status = "B"
					people[j].change_date = i
			return
	return
