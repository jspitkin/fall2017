import sys
from collections import defaultdict

train_file = tuple(open(sys.argv[1], "r"))
test_file = tuple(open(sys.argv[2], "r"))
loc_file = tuple(open(sys.argv[3], "r"))

word_list = pos_list = ftype = f = []
loc = []
feature = defaultdict(list)
label = defaultdict(list)
label['O'] = 0
label['B-PER'] = 1
label['I-PER'] = 2
label['B-LOC'] = 3
label['I-LOC'] = 4
label['B-ORG'] = 5
label['I-ORG'] = 6

def generate(f1, f2, f3, f4, f5, f6, f7):
    prev_word = 'PHI'
    prev_pos = 'PHIPOS'
    if f7 == 1:
	for i in range(len(loc_file)):
		s = loc_file[i]
		s = s.strip()
		loc.append(s)
    with open("train.txt.readable", "w") as out_file:
	for i in range(len(train_file)):
	    l = train_file[i].split()
            if l == []:
		prev_word = 'PHI'
                prev_pos = 'PHIPOS'
            else:
                l_next = train_file[i+1]
		l_next = l_next.split()
                if l_next == []:
                    next_word = 'OMEGA'
                    next_pos = 'OMEGAPOS'
                else:
                    next_word = l_next[2]
                    next_pos = l_next[1]
                    word_list.append(l[2])
                    pos_list.append(l[1])
                    out_file.write('WORD:' + ' ' + l[2] + '\n')
                    if f2 == 1:
                        out_file.write('WORDCON:' + ' ' + prev_word + ' ' + next_word + '\n')
                    else:
                        out_file.write('WORDCON: n/a' + '\n')
                    if f3 == 1:
                        out_file.write('POS:' +  ' ' + l[1] + '\n')
                    else:
                        out_file.write('POS: n/a' + '\n')
                    if f4 == 1:
                        out_file.write('POSCON:' + ' ' + prev_pos + ' ' + next_pos + '\n')
                    else:
                        out_file.write('POSCON: n/a' + '\n')
                    if f5 == 1:
                        word = l[2]
                        if (word[-1] == '.' and '.' in word and len(word) <= 4):
                            out_file.write('ABBR: yes' + '\n')
                        else:
                            out_file.write('ABBR: no' + '\n')
                    else:
                        out_file.write('ABBR: n/a' + '\n')
                    if f6 == 1:
                        first_letter = l[2][0]
                        if first_letter.isupper():
                            out_file.write('CAPS: yes' + '\n')
                        else:
                            out_file.write('CAPS: no' + '\n')
                    else:
                        out_file.write('CAPS: n/a' + '\n')
                    if f7 == 1:
                        if l[2] in loc:
                            out_file.write('LOCATION: yes' + '\n')
                        else:
                            out_file.write('LOCATION: no' + '\n')
                    else:
                        out_file.write('LOCATION: n/a' + '\n')
                    out_file.write('\n')
                    prev_word = l[2]
                    prev_pos = l[1]
    x = 1
    for i in xrange(len(train_file)):
        l2 = train_file[i].split()
        if l2:
            w = 'word-' + l2[2]
            if w not in feature:
                feature[w] = x
                x = x + 1
	feature['word-UNK'] = x
	x = x + 1
    if f2 == 1:
        for i in xrange(len(train_file)):
            l2 = train_file[i].split()
            if len(l2) != 0:
                prev_line = train_file[i-1]
		prev_line = prev_line.split()
                if prev_line == [] or i==1:
                    prev_word = 'prev-word-PHI'
                else:
                    prev_word = 'prev-word-' + prev_line[2]
                next_line = train_file[i+1]
		next_line = next_line.split()
                if next_line == []:
                    next_word = 'next-word-OMEGA'
                else:
                    next_word = 'next-word-' + next_line[2]
                if prev_word not in feature:
                    feature[prev_word] = x
                    x = x + 1
                if next_word not in feature:
                    feature[next_word] = x
                    x = x + 1
	feature['prev-word-UNK'] = x
	x = x + 1
	feature['next-word-UNK'] = x
	x = x + 1
    if f3 == 1:
        for i in xrange(len(train_file)):
            l2 = train_file[i].split()
            if l2:
                p = 'pos-' + l2[1]
                if p not in feature:
                    feature[p] = x
                    x = x + 1
	feature['pos-UNKPOS'] = x
	x = x + 1
    if f4 == 1:
        for i in xrange(len(train_file)):
            l2 = train_file[i].split()
            if len(l2) != 0:
                prev_line = train_file[i-1]
		prev_line = prev_line.split()
                if prev_line == [] or i==1:
                    prev_pos = 'prev-pos-PHIPOS'
                else:
                    prev_pos = 'prev-pos-' + prev_line[1]
                next_line = train_file[i+1]
		next_line = next_line.split()
                if next_line == []:
                    next_pos = 'next-pos-OMEGAPOS'
                else:
                    next_pos = 'next-pos-' + next_line[1]
                if prev_pos not in feature:
                    feature[prev_pos] = x
                    x = x + 1
                if next_pos not in feature:
                    feature[next_pos] = x
                    x = x + 1
	feature['prev-pos-UNKPOS'] = x
	x = x + 1
	feature['next-pos-UNKPOS'] = x
	x = x + 1
    if f5 == 1:
        feature['abbreviation'] = x
        x = x + 1
    if f6 == 1:
        feature['capitalized'] = x
        x = x + 1
    if f7 == 1:
        feature['location'] = x
    with open("train.txt.vector", "w") as out_file:
        for i in range(len(train_file)):
            del f[:]
 	    t = train_file[i].split()
            if t != []:
                key = t[0]
                la = label[key]
                la = str(la)
                word1 = 'word-' + t[2]
                if word1 in feature:
                    f.append(feature[word1])
                if f2 == 1:
                    prev_line = train_file[i - 1]
		    prev_line = prev_line.split()
                    if i == 1 or prev_line == []:
                        prev_word = 'prev-word-PHI'
                    else:
                        prev_word = 'prev-word-' + prev_line[2]
                    next_line = train_file[i+1]
		    next_line = next_line.split()
                    if next_line == []:
                        next_word = 'next-word-OMEGA'
                    else:
                        next_word = 'next-word-' + next_line[2]
                    f.append(feature[prev_word])
                    f.append(feature[next_word])
                if f3 == 1:
                    pos = 'pos-' + t[1]
                    f.append(feature[pos])
                if f4 == 1:
                    prev_line = train_file[i-1]
		    prev_line = prev_line.split()
                    if prev_line == [] or i==1:
                        prev_pos = 'prev-pos-PHIPOS'
                    else:
                        prev_pos = 'prev-pos-' + prev_line[1]
                    next_line = train_file[i+1]
		    next_line = next_line.split()
                    if next_line == []:
                        next_pos = 'next-pos-OMEGAPOS'
                    else:
                        next_pos = 'next-pos-' + next_line[1]
                    f.append(feature[prev_pos])
                    f.append(feature[next_pos])
                if f5 == 1:
                    word = t[2]
                    if (word[-1] == '.' and len(word) <= 4 and '.' in word):
                        f.append(feature['abbreviation'])
                if f6 == 1:
                    first_letter = t[2][0]
                    if first_letter.isupper():
                        f.append(feature['capitalized'])
                if f7 == 1:
                    if t[2] in loc:
                        f.append(feature['location'])
                if len(f) == 1:
                    out_file.write(la + ' ')
                    f[0] = str(f[0])
                    out_file.write(f[0] + ':1' + ' ')
                else:
                    f.sort()
                    out_file.write(la + ' ')
                    for j in range(len(f)):
                        f[j] = str(f[j])
                        out_file.write(f[j] + ':1' + ' ')
                out_file.write("\n")

    with open("test.txt.readable", "w") as out_file:
        for i in range(len(test_file)):
            l = test_file[i].split()
            if l == []:
                prev_word = 'PHI'
                prev_pos = 'PHIPOS'
            else:
                l_next = test_file[i+1]
                l_next = l_next.split()
                if l_next == []:
                    next_word = 'OMEGA'
                    next_pos = 'OMEGAPOS'
                else:
                    next_word = l_next[2]
                    next_pos = l_next[1]
                    if next_word not in word_list:
                        next_word = 'UNK'
                    if next_pos not in pos_list:
                        next_pos = 'UNKPOS'
                    out_file.write('WORD:' + ' ' + l[2] + '\n')
                    if f2 == 1:
                        out_file.write('WORDCON:' + ' ' + prev_word + ' ' + next_word + '\n')
                    else:
                        out_file.write('WORDCON: n/a' + '\n')
                    if f3 == 1:
                        out_file.write('POS:' +  ' ' + l[1] + '\n')
                    else:
                        out_file.write('POS: n/a' + '\n')
                    if f4 == 1:
                        out_file.write('POSCON:' + ' ' + prev_pos + ' ' + next_pos + '\n')
                    else:
                        out_file.write('POSCON: n/a' + '\n')
                    if f5 == 1:
                        word = l[2]
                        if (word[-1] == '.' and '.' in word and len(word) <= 4):
                            out_file.write('ABBR: yes' + '\n')
                        else:
                            out_file.write('ABBR: no' + '\n')
                    else:
                        out_file.write('ABBR: n/a' + '\n')
                    if f6 == 1:
                        first_letter = l[2][0]
                        if first_letter.isupper():
                            out_file.write('CAPS: yes' + '\n')
                        else:
                            out_file.write('CAPS: no' + '\n')
                    else:
                        out_file.write('CAPS: n/a' + '\n')
                    if f7 == 1:
                        if l[2] in loc:
                            out_file.write('LOCATION: yes' + '\n')
                        else:
                            out_file.write('LOCATION: no' + '\n')
                    else:
                        out_file.write('LOCATION: n/a' + '\n')
                out_file.write('\n')
                prev_word = l[2]
                prev_pos = l[1]
    with open("test.txt.vector", "w") as out_file:
        for i in range(len(test_file)):
            del f[:]
            t1 = test_file[i].split()
            if t1 != []:
                key = t1[0]
                la = label[key]
                la = str(la)
                word1 = 'word-' + t1[2]
                if word1 in feature:
                    f.append(feature[word1])
                else:
                    f.append(feature['word-UNK'])
                if f2 == 1:
                    prev_line = test_file[i - 1]
                    prev_line = prev_line.split()
                    if i == 1 or prev_line == []:
                        prev_word = 'prev-word-PHI'
                    else:
                        prev_word = 'prev-word-' + prev_line[2]
                    next_line = test_file[i+1]
                    next_line = next_line.split()
                    if next_line == []:
                        next_word = 'next-word-OMEGA'
                    else:
                        next_word = 'next-word-' + next_line[2]
		    if prev_word in feature:
                    	f.append(feature[prev_word])
		    else:
			f.append(feature['prev-word-UNK'])
		    if next_word in feature:
                    	f.append(feature[next_word])
		    else:
			f.append(feature['next-word-UNK']) 
                if f3 == 1:
                    pos = 'pos-' + t1[1]
                    if pos in feature:
                        f.append(feature[pos])
                    else:
                        f.append(feature['pos-UNKPOS'])
                if f4 == 1:
                    prev_line = test_file[i-1]
                    prev_line = prev_line.split()
                    if prev_line == [] or i==1:
                        prev_pos = 'prev-pos-PHIPOS'
                    else:
                        prev_pos = 'prev-pos-' + prev_line[1]
                    next_line = test_file[i+1]
                    next_line = next_line.split()
                    if next_line == []:
                        next_pos = 'next-pos-OMEGAPOS'
                    else:
                        next_pos = 'next-pos-' + next_line[1]
		    if prev_pos in feature:
                    	f.append(feature[prev_pos])
		    else:
			f.append(feature['prev-pos-UNKPOS'])
		    if next_pos in feature:
                    	f.append(feature[next_pos])
		    else:
			f.append(feature['next-pos-UNKPOS']) 
                if f5 == 1:
                    word = t1[2]
                    if (word[-1] == '.' and '.' in word and len(word) <= 4):
                        f.append(feature['abbreviation'])
                if f6 == 1:
                    first_letter = t1[2][0]
                    if first_letter.isupper():
                        f.append(feature['capitalized'])
                if f7 == 1:
                    if t1[2] in loc:
                        f.append(feature['location'])
                if len(f) == 1:
                    out_file.write(la + ' ')
                    f[0] = str(f[0])
                    out_file.write(f[0] + ':1' + ' ')
                else:
                    f.sort()
                    out_file.write(la + ' ')
                    for j in range(len(f)):
                        f[j] = str(f[j])
                        out_file.write(f[j] + ':1' + ' ')
                out_file.write("\n")

def main():
    for i in range(len(sys.argv)):
        if i >= 4:
            ftype.append(sys.argv[i])
    f1 = 1
    f2 = f3 = f4 = f5 = f6 = f7 = 0
    if 'WORDCON' in ftype:
        f2 = 1
    if 'POS' in ftype:
        f3 = 1
    if 'POSCON' in ftype:
        f4 = 1
    if 'ABBR' in ftype:
        f5 = 1
    if 'CAP' in ftype:
        f6 = 1
    if 'LOCATION' in ftype:
        f7 = 1
    generate(f1, f2, f3, f4, f5, f6, f7)

if __name__ == '__main__':
    main()
