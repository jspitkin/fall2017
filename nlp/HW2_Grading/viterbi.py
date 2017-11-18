
import sys 
import math
def readInput(filename):
	data = []
	with open(filename) as doc:
		for line in doc:
			line = line.strip()
			line = line.lower()
			line = line.split()
			data.append(line)
	return data
def viterbi(pos_tag, word_tag, line) :
	probability_word = {}
	score = {}
	backPtr = {}
	maxScore = {}
	maxTag = {}
	seq = {}
	pos = ['noun','verb','inf','prep']
	i = 0 
	for tag in pos:
		if word_tag.has_key((line[0],tag)) and pos_tag.has_key((tag,'phi')):
			score[(i,tag,line[0])] = math.log(float(word_tag[(line[0],tag)]),2) + math.log(float(pos_tag[(tag,'phi')]),2)
		elif word_tag.has_key((line[0],tag)):
			score[(i,tag,line[0])] = math.log(float(word_tag[(line[0],tag)]),2) +	math.log(float(0.0001),2)
		elif pos_tag.has_key((tag,'phi')):
			score[(i,tag,line[0])] = math.log(float(0.0001),2) + math.log(float(pos_tag[(tag,'phi')]),2)
		else :
			score[(i,tag,line[0])] = 2*(math.log(float(0.0001),2))
		backPtr[(i,tag, line[0])] = 0

	for Word in line[1:]:
		i = i+1
		for tag in pos:
			maxScore[Word] = -100
			for tag1 in pos:
				if pos_tag.has_key((tag,tag1)):
					scoretemp =  score[(i-1,tag1 ,line[i-1])] + math.log(float(pos_tag[(tag,tag1)]),2)
					if scoretemp > maxScore[Word] :
						maxScore[Word] = scoretemp
						backPtr[(i,tag, Word)] = tag1
			
					#print Word,tag1,maxScore,scoretemp
			if word_tag.has_key((Word,tag)) :
				score[(i,tag,Word)] = math.log(float(word_tag[(Word,tag)]),2) + maxScore[Word]
			else :
				score[(i,tag,Word)] =  math.log(float(0.0001),2) + maxScore[Word]
	i = len(line)-1
	seq[(i,line[-1])] = 'noun'
	for tag in pos:
		if score[(i,tag,line[-1])] > score[(i,seq[(i,line[-1])],line[-1])]:
			seq[(i,line[-1])] = tag
	i = i-1 
	temp_line = line[::-1]
	for j in range (1, len(line)):
		seq[(i,temp_line[j])] = backPtr[(i+1,seq[(i+1,temp_line[j-1])],temp_line[j-1])]
		i = i-1
	#print seq
			
		#score[(Word,tag)] = word_tag[(Word,tag)] 
	i=-1
	print "PROCESSING SENTENCE:"," ".join(line) 
	print "\nFINAL VITERBI NETWORK" 
	for Word in line:
		i=i+1
		for tag in pos:
			print "P(%s=%s)"%(Word,tag) ,"= %0.4f"%score[(i,tag,Word)]
			#print Word, tag ,backPtr[(i,tag, Word)]''
	maxTag[line[-1]] = 'noun'
	for tag in pos :
		if score[(len(line)-1,tag,line[-1])] > score[(len(line)-1,maxTag[line[-1]],line[-1])]:
			maxTag[line[-1]] = tag
	i = 0
	print "\nFINAL BACKPTR NETWORK" 
	for Word in line[1:]:
		i = i+1
		for tag in pos:
			print "Backptr(%s=%s)"%(Word,tag) ,"=",backPtr[(i,tag,Word)]
	
	print "\nBEST TAG SEQUENCE HAS LOG PROBABILITY = %0.4f"%score[(len(line)-1,maxTag[line[-1]],line[-1])]
	i = len(line)
	for Word in line[::-1]:
		i = i-1
		print Word, "->",seq[(i,Word)]
	'''BEST TAG SEQUENCE HAS LOG PROBABILITY = -10.4238
fish -> verb
bears -> noun
'''

		#

	#print pos_tag[('noun','phi')]

	#for line in sentence_file:
	#	for Word in line[1:]:

def create_tag(probability):
	pos = ['noun','verb','inf','prep']
	pos_tag = {}
	word_tag = {}
	for rows in probability:
		if rows[0] in pos  :
			pos_tag.update({(rows[0],rows[1]) :rows[2]})
		else :
			word_tag.update({(rows[0],rows[1]) :rows[2]})
	for tag1 in pos:
		for tag2 in pos:
			if not pos_tag.has_key((tag1,tag2)):
				pos_tag[(tag1,tag2)] = 0.0001
	return pos_tag, word_tag

def forward(pos_tag, word_tag,line):
	probability_word = {}
	seqSum = {}
	backPtr = {}
	maxScore = {}
	maxTag = {}
	seq = {}
	summation_word = {}
	pos = ['noun','verb','inf','prep']
	i = 0
	for tag in pos:
		if word_tag.has_key((line[0],tag)) and pos_tag.has_key((tag,'phi')):
			seqSum[(i,tag, line[0])] = float(word_tag[(line[0],tag)] )* float(pos_tag[(tag,'phi')])
		elif pos_tag.has_key((tag,'phi')):
			seqSum[(i,tag, line[0])] = 0.0001* float(pos_tag[(tag,'phi')])
		elif word_tag.has_key((line[0],tag)):
			seqSum[(i,tag, line[0])] = float(word_tag[(line[0],tag)] )* 0.0001
		else :
			seqSum[(i,tag, line[0])] = 0.0001 * 0.0001
	for Word in line[1:]:
		i = i+1
		for tag in pos:
			summation= 0
			for tag1 in pos:
				summation = summation+(seqSum[(i-1,tag1,line[i-1])]*float(pos_tag[tag,tag1]))

				if word_tag.has_key((Word,tag)): 
					seqSum[(i,tag,Word)] = float(word_tag[(Word,tag)])*summation
				else:
					seqSum[(i,tag,Word)] = 0.0001*summation
			
	i = -1
	for Word in line:
		i = i+1
		summation1 = 0
		for tag1 in pos:
			summation1 = summation1 + seqSum[(i,tag1,Word)]
		
		for tag in pos:
			probability_word[(i,Word,tag)] = seqSum[(i,tag,Word)]/summation1
	print "\nFORWARD ALGORITHM RESULTS"
	i = -1
	for Word in line:
		i = i+1
		for tag in pos:
			#print Word
			print "P(%s=%s)"%(Word,tag) ,"= %0.4f" %probability_word[(i,Word,tag)]

	print "\n"






	
	
	


def main():
	try:
		probability = readInput(sys.argv[1])
		pos_tag, word_tag = create_tag(probability)
		sentence_file = readInput(sys.argv[2])
		for sentence in sentence_file:
			viterbi(pos_tag, word_tag,sentence)
			forward(pos_tag, word_tag,sentence)
	except Exception as e:
		print "2 command line arguments needed as - probs.txt sents.txt"
	
	
main()


