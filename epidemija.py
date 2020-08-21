from random import seed, randint, random, gauss, choice
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from epipy import *

seed(datetime.now())

######  PARAMETERS  ######
N = 10000					#Število ljudi
average_people_per_unit = 3
stdev = 2
t = 200		#Število dni
kuzna_doba = 9
bolna_doba = 13
a1 = 0.15		#a1=0.10
a2 = 0.05		#
da = 0.01		#dt=0.03
bt = [0.03,0.08,0.14,0.17,0.17,0.14,0.1,0.06,0.03,0.01,1,1,1,1,1,1,1]	#Verjetnost, da K => B
bt1 = [0.01,0.03,0.08,0.14,0.17,0.17,0.14,0.1,0.06,0.03,1,1,1,1,1,1,1]
bt2 = [0.01,0.01,0.03,0.08,0.14,0.17,0.17,0.14,0.1,0.06,1,1,1,1,1,1,1]
bt3 = [0.01,0.01,0.01,0.03,0.08,0.14,0.17,0.17,0.14,0.8,1,1,1,1,1,1,1]

states = ["D", "K", "B", "O"]

b_p = []
for i in range(len(bt)):
	a = 1
	for j in range(i):
		a *= (1-bt[j])
	b_p.append(a)

###########################


def epidemija(N, a1, a2, bt, b_p, v):	#v - številka simulacije; a1 - začetni parameter a; a2 - končno parameter a2
	cells = []
	stats = []				#Array [D, K, B, O] za vsak dan
	people = []
	hist_people = []
	karantena_state = 0
	M = 0		#Število celic
	k = 0
	while k < N:				#Seperate people into cells
		n = gauss(average_people_per_unit, stdev)
		if (10 >= int(n) > 0):
			start = k
			for j in range(int(n)):
				if (k < N):
					people.append(Person(M))
					k += 1
			stop = k-1
			cells.append(Cell(start, stop))
			M += 1	#cell number


	#Initial conditions
	seed(datetime.now())
	people[randint(0, N)].status = "K"


	for i in range(t):
		stats.append(calculate_grid_stats(people, states, N))
		last_stat = stats[-1]

		hist_people_i = []
		for k in people:
			for s in range(len(states)):
				if (k.status == states[s]):
					hist_people_i.append(s)
		hist_people.append(hist_people_i)

		#####   Karantena    ######
		dan_karantene = 50
		if (karantena_state):
			if (i == dan_karantene):
				a1 = a1/10
				a2 = a2/10

		#####


		#####   Person level  #####
		for person in people:
			if (person.status == "K" and (i-person.change_date) >= kuzna_doba):	# K->O, Ki->O
				person.status = "O"
				person.date = i
			if (person.status == "B" and (i-person.change_date) >= bolna_doba):		# B->O
				person.status = "O"
				person.date = i
			if (person.status == "K" or person.status == "Ki"):
				if (outcome(bt[i-person.change_date])):
					person.status = "B"
					person.date = i

		#####   Cell level   #####
		for cell in cells:
			if (cell.status == "D"):		#  Dc -> Kc,  D -> Ki
				check_if_any_K(cell, i, people)
			else if (cell.status == "K"):
				check_if_any_B(cell, i, people)
			else if (cell.status == "B"):
				check_all_for_type(cell, i, people, "O")

		#####   General level   #####
		dK = round((a1*stats[i][1]+a2*stats[i][2])*stats[i][0]*N)
		all_D = []
		for k in range(len(cells)):
			if (cells[k].status == "D"):		#Kaj če lahko zbolijo tudi ozdraveli?
				all_D.append(k)
		for k in range(dK):
			if (len(all_D) != 0):
				seed(datetime.now())
				a = choice(all_D)
				b = randint(cells[a].start, cells[a].stop)
				people[b].status = "K"
				people[b].change_date = i

	while (stats[-2][1] == 0.0 and stats[-2][2] == 0.0):
		stats.pop()
		hist_people.pop()
	D = []
	K = []
	B = []
	O = []
	Ki = []
	for k in stats:
		D.append(k[0])
		K.append(k[1])
		B.append(k[2])
		O.append(k[3])
	stats_per_state = []
	stats_per_state.append(D)
	stats_per_state.append(K)
	stats_per_state.append(B)
	stats_per_state.append(O)

	final_state_str = ("Končno stanje - Dovzetni " + str(round(stats[-1][0]*100, 2)) + "% - Kužni " +
								str(round(stats[-1][1]*100, 2)) + "% - Bolani " +
								str(round(stats[-1][2]*100, 2)) + "% - Ozdraveli " +
								str(round(stats[-1][3]*100, 2)) + "%")
	max_str = ("Max bolni " + str(round(max(B)*100,2)) + "% - Max kužni " + str(round(max(K)*100,2)) + " %")
	parametri = ("Število ljudi {}, a1 {}%, a2 {}%, kužna doba {} dni, bolna doba {} dni".format(N, (a1)*100, a2*100, kuzna_doba, bolna_doba))
	epidemija_len = ("Trajanje epidemije: " + str(len(D)) + " dni")

	# Prikaz rezultatov
	
	# Personal spread
	hist_people = np.array(hist_people)
	plt.xlabel("Številka osebe")
	plt.ylabel("Dnevi po začetku epidemije")
	plt.title("Širjenje bolezni pri posameznih ljudeh")
	plt.imshow(hist_people[:,:50], cmap=mpl.colors.ListedColormap(["tab:green", "tab:orange", "tab:red", "tab:blue"]))
	plt.savefig("Personal_spread_{}".format(v+1))
	plt.clf()

	# Cell distribution
	cell_dist_hist = np.zeros(10)
	for unit in cells:
		cell_dist_hist[int(unit.stop - unit.start)] += 1
	p = [1,2,3,4,5,6,7,8,9,10]
	plt.bar(p, normalize_array(cell_dist_hist))
	plt.xticks(p, p)
	plt.xlabel("Število ljudi v celici")
	plt.ylabel("Delež prebivalstva")
	plt.title("Porazdelitev prebivalstva po celicah\n Srednja vrednost: {}, standardni odklon: {}".format(average_people_per_unit, stdev))
	plt.savefig("Cell_distribution_{}".format(v+1))
	plt.clf()

	# Disease progression
	while (bt[-1] == 1):
		bt.pop()
	plt.plot(np.arange(1, len(bt)+1, 1), bt)
	plt.xlabel("Število dni po okužbi")
	plt.ylabel("Verjetnost da okužena oseba zboli")
	plt.xticks(p, p)
	plt.title("Porazdelitev verjetnosti obolelosti od nastopa okužbe")
	plt.savefig("Disease_progression")
	plt.clf()

	# Epidemic progression
	#plt.title(final_state_str + "\n" + max_str + "\n" + parametri + "\n" + epidemija_len)
	plt.plot(O, label="Ozdraveli {}%".format(round(stats[-1][3]*100, 1)))
	plt.plot(K, label="Kužni {}%".format(round(max(K)*100,1)))
	plt.plot(D, label="Dovzetni {}%".format(round(stats[-1][0]*100, 1)))
	plt.plot(B, label="Bolni {}%".format(round(max(B)*100,1)))
	plt.title("Potek epidemije (trajanje {} dni)\n a1 = {}".format(len(D), a1))
	plt.xlabel("Število dni")
	plt.ylabel("Delež prebivalstva")
	if karantena_state:
		plt.axvline(x=dan_karantene, color="m", linestyle="--")
	plt.legend()
	plt.savefig("Epidemic_progression_{}".format(v+1))
	plt.clf()
	#plt.show()

	print(final_state_str)
	print(max_str)
	print(parametri)
	print(epidemija_len)

	return stats_per_state



def main():
	for r in range(1):
		epidemija(N, a1, a2, bt, b_p, 30)


if __name__ == "__main__":
	main()
