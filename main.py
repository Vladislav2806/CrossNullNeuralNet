from asyncore import read
from tkinter import*
from random import randint
import numpy

def doPlay(x, y, BotOrPlayer):
	global objects, crossPng, nullPng, card, firstGame
	summ = 0
	for i in range(3):
		for j in range(3):
			if card[i][j]==0:
				summ += 1
	if summ<2:
		newGame()

	if BotOrPlayer==0:
		card[y][x] = 1
		cnv.delete(objects[y][x])
		objects[y][x] = cnv.create_image(100+x*200, 100+y*200, image=crossPng)
	else:
		if objects[y][x]!=0:
			newGame()
		else:
			cnv.delete(objects[y][x])
			objects[y][x] = cnv.create_image(100+x*200, 100+y*200, image=nullPng)

def eventManager(event):
	global games, maxGaming
	doPlay(event.x//200, event.y//200, 0)
	neuroLink()

def newGame():
	global objects, card, games, state, sw, firstGame
	for i in range(3):
		for j in range(3):
			cnv.delete(objects[i][j])
			objects[i][j] = 0
			card[i][j] = 0

	#if firstGame:
	#	writeToFile(sw)
	games += 1

def getParams():
	global card
	params = []
	for i in range(3):
		for j in range(3):
			if card[i][j]==0:
				params.append(0)
			elif card[i][j]==1:
				params.append(0.5)
			elif card[i][j]==2:
				params.append(1)
	print(params)
	return params

def writeToFile(sw):
	f = open("SinapticWeigths.txt", "w")
	string = ""
	for i in range(len(sw)):
		for j in range(len(sw[i])):
			for k in range(len(sw[i][j])):
				string += f"{sw[i][j][k]}"
				if k!=len(sw[i][j])-1:
					string += "#"
			if j!=len(sw[i])-1:
				string += "@"
		string += "\n"

	f.write(string)
	f.close()

def readFile(file):
	f = open(f"{file}.txt", "r")
	read = f.read()
	f.close()

	one = read.split("\n")
	for i in range(len(one)):
		one[i] = one[i].split("#")
		for j in range(len(one[i])):
			if one[i][j]=="0.5":
				one[i][j] = 0.5
			else:
				one[i][j] = int(one[i][j])

	return one

def getOut(param):
	return [param.index(max(param))%3, param.index(max(param))//3]

def readSw():
	f = open("SinapticWeigths.txt", "r")
	read = f.read()
	read = read.split("\n")
	sinw = []
	for i in range(len(read)-1):
		sinw.append([])
		read[i] = read[i].split("@")
		for j in range(len(read[i])):
			read[i][j] = read[i][j].split("#")
			sinw[i].append([])
			for k in range(len(read[i][j])):
				if read[i][j][k]!='':
					sinw[i][j].append(float(read[i][j][k]))
	f.close()
	return sinw

def sigmoid(x):
	return 1 / (1+numpy.exp(-x))

def func(x):
	return x*(1-x)

def eventTraining(event):
	global games, firstGame, maxGaming
	if games<=maxGaming and firstGame:
		doPlay(event.x//200, event.y//200, 1)
		neuroLink(event.x//200+event.y//200*3)

def neuroLink():
	global training, answers, sw, objects, games, firstGame, maxGaming
	in_param = getParams()
	fyx = []
	for i in range(5):
		fyx.append([])
		for j in range(9):
			fyx[i].append(0)
			for k in range(9):
				if i==0:
					fyx[i][j] += sw[i][j][k]*in_param[k]
				else:
					fyx[i][j] += sw[i][j][k]*fyx[i-1][k]
			fyx[i][j] = sigmoid(fyx[i][j])

	z = getOut(fyx[-1])
	print(fyx[-1])
	card[z[1]][z[0]] = 2
	doPlay(*z, 1)
	return 0

def startLearning():
	global sw
	training = readFile("Primers")
	answers = readFile("Answers")
	L = 0.4 # можно поэксперементировать
	for h in range(1000):
		for a in range(30):
			x, y = training[a], answers[a]
			fyx = []
			for i in range(5):
				fyx.append([])
				for j in range(9):
					fyx[i].append(0)
					for k in range(9):
						if i==0:
							fyx[i][j] += sw[i][j][k]*x[k]
						else:
							fyx[i][j] += sw[i][j][k]*fyx[i-1][k]
					fyx[i][j] = sigmoid(fyx[i][j])

			delta = [[]]
			for i in range(len(fyx[-1])):
				error = fyx[-1][i]-y[i]
				delta[0].append(error*fyx[-1][i]*(1-fyx[-1][i]))

			for i in range(9):
				for j in range(9):
					sw[-1][i][j] -= L*delta[0][i]*fyx[-2][j]

			for i in range(-3, 1, 1):
				i = abs(i)
				delta.append([])
				for j in range(9):
					q = 0
					for k in range(9):
						q += delta[abs(i-3)][k]*sw[i+1][k][j]
					delta[-1].append(q*func(fyx[i][j]))
					for k in range(9):
						if i==0:
							sw[i][j][k] -= delta[-1][j]*L*x[k]
						else:
							sw[i][j][k] -= delta[-1][j]*L*fyx[i-1][k]

		print(h)
	writeToFile(sw)

root = Tk()

root.title("Neuro Game")
root.geometry("600x600")

cnv = Canvas(width=600, height=600)
cnv.pack()

backPng = PhotoImage(file="Images/BackGround.png")
crossPng = PhotoImage(file="Images/Cross.png")
nullPng = PhotoImage(file="Images/Null.png")
background = cnv.create_image(300, 300, image=backPng)
root.bind("<Button-1>", eventManager)

objects = []
card = []
games = 0
firstGame = 1
maxGaming = 0

sw = readSw()
#for i in range(5):
#	sw.append([])
#	for j in range(9):
#		sw[i].append([])
#		for k in range(9):
#			sw[i][j].append(numpy.random.normal())

for i in range(3):
	objects.append([])
	card.append([])
	for j in range(3):
		card[i].append(0)
		objects[i].append(0)

#startLearning()
root.mainloop()