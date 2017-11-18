import argparse
import sys
import getopt
import math
import re
import random

#Main----------------------------------------------------------
def main(argv):
	#print("Hello world")
	#print(argv)
	'''
	print("------------------------------------------------------")
	print("----------------Hong Xu NLP Program 1-----------------")
	print("------------------------------------------------------")
	print("---------------Professor Ellen Riloff-----------------")
	print("------------------------------------------------------")
	'''
	#Training

	fileTrain = argv[0]#"input/train.txt"
	
	linesTrain = parseFile(fileTrain)

	uni = findUnigrams(linesTrain)
	
	bigramUnsmooth = findBigrams(linesTrain)

	bigramSmooth, startsWith = findBigramsSmooth(linesTrain, len(uni))
	
	if(argv[1] == "-test"):

		#Testing

		fileTest = argv[2]#"input/test.txt"

		linesTest = parseFile(fileTest)

		linesPrint = parseFileLines(fileTest)

		test(linesTest,linesPrint, uni, bigramUnsmooth, bigramSmooth, startsWith, len(uni))

	elif(argv[1] == "-gen"):

		#Generating

		fileGen = argv[2]#"input/seeds.txt"

		wordsGen = parseFileIntoWords(fileGen)

		newBiun = optimizeBiun(bigramUnsmooth)

		gen(wordsGen, newBiun)



#################Generating sentences###############
####################################################
def gen(wGen, biun):
	for w in wGen:
		print("Seed = " + w + "\n")

		s = w.lower()

		for i in range (10):
			print("Sentence ", i+1, ": ", w, end = " " )

			nextWord = s
			wordCount = 1
			while(wordCount < 20 and nextWord != "." and nextWord != "!" and nextWord != "?"):
				rand = random.uniform(0, 1)
				currWord = ""
				currSum = 0
				if(nextWord in biun):
					for word in biun[nextWord]:
						currWord = word.split(" ")[1]
						currSum += 2**biun[nextWord][nextWord + " " + currWord]
						if currSum > rand:
							break
						else:
							key, value = random.choice(list(biun.items()))
							currWord = key
				print(currWord + " ", end = "")
				nextWord = currWord


				wordCount += 1

			print()
		print()

def optimizeBiun(biun):
	newBiun = {}

	for w in biun:
		r = w.split(" ")[0]
		r2 = w.split(" ")[1]
		if(r not in newBiun):
			newBiun[r] = {}
			newBiun[r][w] = biun[w]
		else:
			newBiun[r][w] = biun[w]

	return newBiun


##################Testing Uni/Bigrams###############
####################################################
#Calls the 3 test functions
def test(linesTest, linesP, uni, biun, bism, startsWith, unic):
	i = 0
	for line in linesTest:
		print("S = " + linesP[i] + "\n")
		i+= 1
		testUni(line, uni)
		testBiun(line, biun)
		testBism(line, bism, startsWith, unic)
		print()

#Tests the unigram
def testUni(line, uni):
	prob = 0
	for w in line:
		#if w in uni:
		prob += uni[w]
	print("Unsmoothed Unigrams, logprob(S) =", round(prob, 4))

#Tests unsmooth bigrams
def testBiun(line, biun):
	prob = 0
	if(("\phi " + line[0]) in biun):
		prob += biun[("\phi " + line[0])]
	else:
		print("Unsmoothed Bigrams, logprob(S) = undefined")
		return

	for i in range(0, len(line) -1):
		if(line[i] + " " + line[i+1]) in biun:
			prob += biun[(line[i] + " " + line[i+1])]
		else:
			print("Unsmoothed Bigrams, logprob(S) = undefined")
			return

	print("Unsmoothed Bigrams, logprob(S) =", round(prob, 4))

#Tests smoothed bigrams
def testBism(line, bism, startsWith, unic):
	prob = 0
	if(("\phi " + line[0]) in bism):
		prob += bism[("\phi " + line[0])]
	else:
		r = "\phi"
		prob += math.log((1/(startsWith[r] + unic)), 2)


	for i in range(0, len(line) -1):
		if(line[i] + " " + line[i+1]) in bism:
			prob += bism[(line[i] + " " + line[i+1])]
		else:
			r = line[i].split(" ")
			prob += math.log((1/(startsWith[r[0]] + unic)), 2)
	

	print("Smoothed Bigrams, logprob(S) =", round(prob, 4))


##################Unigram/bigram training###########
####################################################
#Computes a dictionary of unigrams
def findUnigrams(lines):
	uniqueWords = {}
	
	totalCount = 0


	for line in lines:
		for word in line:
			if word not in uniqueWords:
				uniqueWords[word] = 1
			else:
				uniqueWords[word] += 1

	#print(uniqueWords)

	for w in uniqueWords:
		totalCount += uniqueWords[w]

	

	for w in uniqueWords:
		uniqueWords[w] = uniqueWords[w]/totalCount
		
	#print("uniquewords", len(uniqueWords))

	for w in uniqueWords:
		uniqueWords[w] = math.log(uniqueWords[w],2)

	#print(uniqueWords)

	return uniqueWords

#Computes a dictionary of unsmoothed bigrams
def findBigrams(lines):
	pairsOfWords = {}
	startsWith = {}
	startsWith["\phi"] = 1

	for w in lines:
		startsWith["\phi"] += 1
		if(("\phi " + w[0]) not in pairsOfWords): 
			pairsOfWords["\phi " + w[0]] = 1
		else:
			pairsOfWords["\phi " + w[0]] += 1

		for i in range(0, len(w) - 1):
			if(w[i] not in startsWith):
				startsWith[w[i]] = 1
			else:
				startsWith[w[i]] += 1

			if(w[i] + " " + w[i+1]) not in pairsOfWords:
				pairsOfWords[w[i] + " " + w[i+1]] = 1
			else:
				pairsOfWords[w[i] + " " + w[i+1]] += 1

	totalCount = 0

	for w in pairsOfWords:
		totalCount += pairsOfWords[w]
		'''
		if(pairsOfWords[w] > 0):
			print(w)
		'''

	#print(totalCount)

	for w in pairsOfWords:
		r = w.split(" ")
		num = pairsOfWords[w]/startsWith[r[0]]
		pairsOfWords[w] = math.log(num,2)

	#print(pairsOfWords)

	return pairsOfWords

#Computes a dictionary of smoothed bigrams
def findBigramsSmooth(lines, uniC):
	pairsOfWords = {}
	startsWith = {}
	startsWith["\phi"] = 1

	for w in lines:
		startsWith["\phi"] += 1
		if(("\phi " + w[0]) not in pairsOfWords): 
			pairsOfWords["\phi " + w[0]] = 1
		else:
			pairsOfWords["\phi " + w[0]] += 1

		for i in range(0, len(w) - 1):

			if(w[i] not in startsWith):
				startsWith[w[i]] = 1
			else:
				startsWith[w[i]] += 1

			if(w[i] + " " + w[i+1]) not in pairsOfWords:
				pairsOfWords[w[i] + " " + w[i+1]] = 1
			else:
				pairsOfWords[w[i] + " " + w[i+1]] += 1

	for w in pairsOfWords:
		r = w.split(" ")
		num = (pairsOfWords[w] + 1)/(startsWith[r[0]] + uniC)
		pairsOfWords[w] = math.log(num,2)

	#print(pairsOfWords)

	return pairsOfWords, startsWith

##################File Parsing######################
####################################################
#Parses a file into lists of lists each [i,j] is a word
def parseFile(filename):
	file = open(filename,"r")

	wordCount = 0
	#print(file.read())
	lines = []
	linecount = 0
	for line in file:
		line = line.rstrip("\n").lower()
		line = re.sub('  ', ' ', line)
		lines.append(line.split(" "))
		

		for w in lines[linecount]:
			w = w.lower()
			wordCount += 1
		
		#print(lines[linecount])
		linecount += 1

	#print(wordCount)

	return lines

#Parses file into lines
def parseFileLines(filename):
	file = open(filename,"r")

	#print(file.read())
	lines = []
	linecount = 0
	for line in file:
		lines.append(line.rstrip("\n"))
		#print(lines[linecount])

	return lines

#Parses file into words
def parseFileIntoWords(filename):
	file = open(filename,"r")

	#print(file.read())
	lines = []
	linecount = 0
	for line in file:
		lines.append(line.rstrip("\n"))
		#print(lines[linecount])

	return lines



#--------------------------------------------------------------



if __name__ == "__main__":
   main(sys.argv[1:])