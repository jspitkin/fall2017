# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 17:56:46 2017

@author: Raghubar
"""
import sys
train_File = sys.argv[1]
test_File = sys.argv[2]
loc_File = sys.argv[3]
ftype = []
ftype.append(sys.argv[4])
for i in range(5,len(sys.argv)):
    ftype.append(sys.argv[i])
#ftype = ['WORD','WORDCON','POS','POSCON','ABBR','CAP','LOCATION']
#ftype = ['WORD','CAP']
count = 0
#fileRead = open('ner-input-files/train.txt')
fileRead = open(train_File)
initialData = fileRead.read()
dataSepInSent = initialData.strip().split('\n\n')
#locRead = open('ner-input-files/locs.txt')
locRead = open(loc_File)
locData = locRead.read()
locSep = locData.strip().split('\n')
labels = {'O': 0, 'B-PER': 1,'I-PER': 2,'B-LOC': 3,'I-LOC': 4,'B-ORG': 5,'I-ORG': 6}
featureList = {}
reverseList = {}
sortFeature = []
featureList["ABBR"] = count+1;
count = count+1
reverseList[count] = "ABBR"
featureList["CAP"] = count+1;
count = count+1
reverseList[count] = "CAP"
featureList["LOCATION"] = count+1;
count = count+1
reverseList[count] = "LOCATION"
featureList["PHI"] = count+1;
count = count+1
reverseList[count] = "PHI"
featureList["PHIPOS"] = count+1;
count = count+1
reverseList[count] = "PHIPOS"
featureList["OMEGA"] = count+1;
count = count+1
reverseList[count] = "OMEGA"
featureList["OMEGAPOS"] = count+1;
count = count+1
reverseList[count] = "OMEGAPOS"
featureList["word*UNK"] = count+1;
count = count+1
reverseList[count] = "word*UNK"
featureList["prev*word*UNK"] = count+1;
count = count+1
reverseList[count] = "prev*word*UNK"
featureList["next*word*UNK"] = count+1;
count = count+1
reverseList[count] = "next*word*UNK"
featureList["pos*UNKPOS"] = count+1;
count = count+1
reverseList[count] = "pos*UNKPOS"
featureList["prev*pos*UNKPOS"] = count+1;
count = count+1
reverseList[count] = "prev*pos*UNKPOS"
featureList["next*pos*UNKPOS"] = count+1;
count = count+1
reverseList[count] = "next*pos*UNKPOS"
prevWord = "PHI"
prevPos = "PHIPOS"
feature = ""
f = open("train.txt.readable","w+")
v = open("train.txt.vector","w+")
for row in dataSepInSent :
    iteration = 0
    newWord = row.strip().split('\n')
    prevWord = "PHI"
    prevPos = "PHIPOS"
    for word in newWord :
        wordArr = word.split()
        if iteration!=0 :
            if "next*word*"+wordArr[2] not in featureList:
                featureList["next*word*"+wordArr[2]] = count+1
                count = count+1
                reverseList[count] = "next*word*"+wordArr[2]
            if "next*pos*"+wordArr[1] not in featureList:
                featureList["next*pos*"+wordArr[1]] = count+1
                count = count+1
                reverseList[count] = "next*pos*"+wordArr[1]
            if "WORDCON" in ftype:
                sortFeature.append(featureList["next*word*"+wordArr[2]])
            if "POSCON" in ftype:
                sortFeature.append(featureList["next*pos*"+wordArr[1]])
        for i in sorted(sortFeature):
            feature = feature+" "+str(i)+":1"
        if iteration!=0:
            v.write(feature+'\n')
        sortFeature = []
        printingFeature = feature.split()
        s = ""
        prevW = ""
        prevP = ""
        nextW = ""
        nextP = ""
        pos = ""
        abbr = "no"
        cap = "no"
        loc = "no"
        for i in printingFeature:
            if ":" in i:
                a = i.split(':')
                reverse = reverseList[int(a[0])].rsplit("*",1)
                abca = reverseList[int(a[0])]
                if "WORD" in ftype and "word"==reverse[0] and iteration!=0:
                    f.write("WORD: "+ reverse[-1])
                    f.write('\n')
                if "WORDCON" in ftype and "prev*word" in reverse:
                    prevW = reverse[-1]
                if "WORDCON" in ftype and "next*word" in reverse :
                    nextW = reverse[-1]
                if "POSCON" in ftype and "prev*pos" in reverse:
                    prevP = reverse[-1]
                if "POSCON" in ftype and "next*pos" in reverse :
                    nextP = reverse[-1]
                if "POS" in ftype and "pos" in reverse:
                    pos = reverse[-1]
                if "ABBR" in ftype and abca in "ABBR":
                    abbr = "yes"
                if "CAP" in ftype and abca in "CAP":
                    cap = "yes"
                if "LOCATION" in ftype and abca in "LOCATION":
                    loc = "yes"
                    
        if iteration!=0 :    
            if "WORDCON" in ftype and prevW!="" and nextW!="":
                f.write("WORDCON: "+prevW+" "+nextW)
                f.write('\n')
            else :
                f.write("WORDCON: n/a")
                f.write('\n')
            if "POS" in ftype and pos !="":
                f.write("POS: "+ pos)
                f.write('\n')
            else :
                f.write("POS: n/a")
                f.write('\n')
            if "POSCON" in ftype and prevP!="" and nextP!="":
                f.write("POSCON: "+prevP+" "+nextP)
                f.write('\n')
            else :
                f.write("POSCON: n/a")
                f.write('\n')
            if "ABBR" in ftype and abbr!="":
                f.write("ABBR: "+abbr)
                f.write('\n')
            else:
                f.write("ABBR: n/a")
                f.write('\n')
            if "CAP" in ftype and cap!="":
                f.write("CAP: "+cap)
                f.write('\n')
            else:
                f.write("CAP: n/a")
                f.write('\n')
            if "LOCATION" in ftype and loc!="":
                f.write("LOCATION: "+loc)
                f.write('\n')
                f.write('\n')
            else:
                f.write("LOCATION: n/a")
                f.write('\n')
                f.write('\n')
       
        feature = ""
        if "word*"+wordArr[2] not in featureList :
            featureList["word*"+wordArr[2]] = count+1
            count = count+1
            reverseList[count] = "word*"+wordArr[2]
        if "next*word*"+wordArr[2] not in featureList :
            featureList["next*word*"+wordArr[2]] = count+1
            count = count+1
            reverseList[count] = "next*word*"+wordArr[2]
        if "prev*word*"+wordArr[2] not in featureList :
            featureList["prev*word*"+wordArr[2]] = count+1
            count = count+1
            reverseList[count] = "prev*word*"+wordArr[2]
        if "pos*"+wordArr[1] not in featureList:
            featureList["pos*"+wordArr[1]] = count+1
            count = count+1
            reverseList[count] = "pos*"+wordArr[1]
        if "prev*pos*"+wordArr[1] not in featureList:
            featureList["prev*pos*"+wordArr[1]] = count+1
            count = count+1
            reverseList[count] = "prev*pos*"+wordArr[1]
        if "next*pos*"+wordArr[1] not in featureList:
            featureList["next*pos*"+wordArr[1]] = count+1
            count = count+1
            reverseList[count] ="next*pos*"+wordArr[1]
        if "prev*word*"+prevWord not in featureList:
            featureList["prev*word*"+prevWord] = count+1
            count = count+1
            reverseList[count] = "prev*word*"+prevWord
        if "prev*pos*"+prevPos not in featureList:
            featureList["prev*pos*"+prevPos] = count+1
            count = count+1
            reverseList[count] = "prev*pos*"+prevPos 
        feature = feature+str(labels[wordArr[0]])
        if "WORD" in ftype:
            sortFeature.append(featureList["word*"+wordArr[2]])
        if "WORDCON" in ftype:
            sortFeature.append(featureList["prev*word*"+prevWord])
        if "POS" in ftype:
            sortFeature.append(featureList["pos*"+wordArr[1]])
        if "POSCON" in ftype:
            sortFeature.append(featureList["prev*pos*"+prevPos])
        if "CAP" in ftype:
            if wordArr[2][0].isupper():
                sortFeature.append(featureList["CAP"])
        if "ABBR" in ftype:
            if len( wordArr[2])<=4 and wordArr[2][len(wordArr[2])-1]=='.':
                abbrNew = wordArr[2].replace(".","")
                if abbrNew.isalpha():
                    sortFeature.append(featureList["ABBR"])
                elif abbrNew == "":
                    sortFeature.append(featureList["ABBR"])
                
        if "LOCATION" in ftype and wordArr[2] in locSep:
            sortFeature.append(featureList["LOCATION"])
        iteration = iteration+1
        prevWord = wordArr[2]
        prevPos = wordArr[1]
    if "next*word*OMEGA" not in featureList:
        featureList["next*word*OMEGA"] = count+1
        count = count+1
        reverseList[count] = "next*word*OMEGA"
    if "next*pos*OMEGAPOS" not in featureList:
        featureList["next*pos*OMEGAPOS"] = count+1
        count = count+1
        reverseList[count] = "next*pos*OMEGAPOS"
    if "WORDCON" in ftype:
        sortFeature.append(featureList["next*word*OMEGA"])
    if "POSCON" in ftype:
        sortFeature.append(featureList["next*pos*OMEGAPOS"])
    for i in sorted(sortFeature):
            feature = feature+" "+str(i)+":1"
    v.write(feature+'\n')
    printingFeature = feature.split()
    prevW = ""
    prevP = ""
    nextW = ""
    nextP = ""
    pos = ""
    abbr = "no"
    cap = "no"
    loc = "no"
    for i in printingFeature:
        if ":" in i:
            a = i.split(':')
            reverse = reverseList[int(a[0])].rsplit("*",1)
            abca = reverseList[int(a[0])]
            if "WORD" in ftype and "word"==reverse[0]:
                f.write("WORD: "+ reverse[-1])
                f.write('\n')
            if "WORDCON" in ftype and "prev*word" in reverse:
                prevW = reverse[-1]
            if "WORDCON" in ftype and "next*word" in reverse :
                nextW = reverse[-1]
            if "POSCON" in ftype and "prev*pos" in reverse:
                prevP = reverse[-1]
            if "POSCON" in ftype and "next*pos" in reverse :
                nextP = reverse[-1]
            if "POS" in ftype and "pos" in reverse:
                pos = reverse[-1]
            if "ABBR" in ftype and abca in "ABBR":
                abbr = "yes"
            if "CAP" in ftype and abca in "CAP":
                cap = "yes"
            if "LOCATION" in ftype and abca in "LOCATION":
                loc = "yes"
                    
    if iteration!=0 :    
        if "WORDCON" in ftype and prevW!="" and nextW!="":
            f.write("WORDCON: "+prevW+" "+nextW)
            f.write('\n')
        else :
            f.write("WORDCON: n/a")
            f.write('\n')
        if "POS" in ftype and pos !="":
            f.write("POS: "+ pos)
            f.write('\n')
        else :
            f.write("POS: n/a")
            f.write('\n')
        if "POSCON" in ftype and prevP!="" and nextP!="":
            f.write("POSCON: "+prevP+" "+nextP)
            f.write('\n')
        else :
            f.write("POSCON: n/a")
            f.write('\n')
        if "ABBR" in ftype and abbr!="":
            f.write("ABBR: "+abbr)
            f.write('\n')
        else:
            f.write("ABBR: n/a")
            f.write('\n')
        if "CAP" in ftype and cap!="":
            f.write("CAP: "+cap)
            f.write('\n')
        else:
            f.write("CAP: n/a")
            f.write('\n')
        if "LOCATION" in ftype and loc!="":
            f.write("LOCATION: "+loc)
            f.write('\n')
            f.write('\n')
        else:
            f.write("LOCATION: n/a")
            f.write('\n')
            f.write('\n')
       
f.close() 
v.close()  
print "hey"
prevWord = "PHI"
prevPos = "PHIPOS"
feature = ""
ft = open("test.txt.readable","w+")
vt = open("test.txt.vector","w+")
fileRead = open(test_File)
initialData = fileRead.read()
dataSepInSent = initialData.strip().split('\r\n\r\n\r\n')
for row in dataSepInSent :
    iteration = 0
    newWord = row.strip().split('\r\n')
    prevWord = "PHI"
    prevPos = "PHIPOS"
    for word in newWord :
        wordArr = word.split()
        if iteration!=0 :
            if "WORDCON" in ftype and "next*word*"+wordArr[2] in featureList:
                sortFeature.append(featureList["next*word*"+wordArr[2]])
            else:
                sortFeature.append(featureList["next*word*UNK"])
            if "POSCON" in ftype and "next*pos*"+wordArr[1] in featureList:
                sortFeature.append(featureList["next*pos*"+wordArr[1]])
            else:
                sortFeature.append(featureList["next*pos*UNKPOS"])
        for i in sorted(sortFeature):
            feature = feature+" "+str(i)+":1"
        if iteration!=0:
            vt.write(feature+'\n')
        sortFeature = []
        printingFeature = feature.split()
        s = ""
        prevW = ""
        prevP = ""
        nextW = ""
        nextP = ""
        pos = ""
        abbr = "no"
        cap = "no"
        loc = "no"
        for i in printingFeature:
            if ":" in i:
                a = i.split(':')
                reverse = reverseList[int(a[0])].rsplit("*",1)
                abca = reverseList[int(a[0])]
                if "WORD" in ftype and "word"==reverse[0] and iteration!=0:
                    ft.write("WORD: "+ reverse[-1])
                    ft.write('\n')
                if "WORDCON" in ftype and "prev*word" in reverse:
                    prevW = reverse[-1]
                if "WORDCON" in ftype and "next*word" in reverse :
                    nextW = reverse[-1]
                if "POSCON" in ftype and "prev*pos" in reverse:
                    prevP = reverse[-1]
                if "POSCON" in ftype and "next*pos" in reverse :
                    nextP = reverse[-1]
                if "POS" in ftype and "pos" in reverse:
                    pos = reverse[-1]
                if "ABBR" in ftype and abca in "ABBR":
                    abbr = "yes"
                if "CAP" in ftype and abca in "CAP":
                    cap = "yes"
                if "LOCATION" in ftype and abca in "LOCATION":
                    loc = "yes"
                    
        if iteration!=0 :    
            if "WORDCON" in ftype and prevW!="" and nextW!="":
                ft.write("WORDCON: "+prevW+" "+nextW)
                ft.write('\n')
            else :
                ft.write("WORDCON: n/a")
                ft.write('\n')
            if "POS" in ftype and pos !="":
                ft.write("POS: "+ pos)
                ft.write('\n')
            else :
                ft.write("POS: n/a")
                ft.write('\n')
            if "POSCON" in ftype and prevP!="" and nextP!="":
                ft.write("POSCON: "+prevP+" "+nextP)
                ft.write('\n')
            else :
                ft.write("POSCON: n/a")
                ft.write('\n')
            if "ABBR" in ftype and abbr!="":
                ft.write("ABBR: "+abbr)
                ft.write('\n')
            else:
                ft.write("ABBR: n/a")
                ft.write('\n')
            if "CAP" in ftype and cap!="":
                ft.write("CAP: "+cap)
                ft.write('\n')
            else:
                ft.write("CAP: n/a")
                ft.write('\n')
            if "LOCATION" in ftype and loc!="":
                ft.write("LOCATION: "+loc)
                ft.write('\n')
                ft.write('\n')
            else:
                ft.write("LOCATION: n/a")
                ft.write('\n')
                ft.write('\n')
       
        feature = ""
        feature = feature+str(labels[wordArr[0]])
        if "WORD" in ftype and "word*"+wordArr[2] in featureList:
            sortFeature.append(featureList["word*"+wordArr[2]])
        else:
            sortFeature.append(featureList["word*UNK"])
        if "WORDCON" in ftype and "prev*word*"+prevWord in featureList:
            sortFeature.append(featureList["prev*word*"+prevWord])
        else:
            sortFeature.append(featureList["prev*word*UNK"])
        if "POS" in ftype and "pos*"+wordArr[1] in featureList:
            sortFeature.append(featureList["pos*"+wordArr[1]])
        else:
            sortFeature.append(featureList["pos*UNKPOS"])
        if "POSCON" in ftype and "prev*pos*"+prevPos in featureList:
            sortFeature.append(featureList["prev*pos*"+prevPos])
        else:
            sortFeature.append(featureList["prev*pos*UNKPOS"])
        if "CAP" in ftype:
            if wordArr[2][0].isupper():
                sortFeature.append(featureList["CAP"])
        if "ABBR" in ftype:
            if len( wordArr[2])<=4 and wordArr[2][len(wordArr[2])-1]=='.':
                abbrNew = wordArr[2].replace(".","")
                if abbrNew.isalpha():
                    sortFeature.append(featureList["ABBR"])
                elif abbrNew == "":
                    sortFeature.append(featureList["ABBR"])
                
        if "LOCATION" in ftype and wordArr[2] in locSep:
            sortFeature.append(featureList["LOCATION"])
        iteration = iteration+1
        prevWord = wordArr[2]
        prevPos = wordArr[1]
    if "WORDCON" in ftype:
        sortFeature.append(featureList["next*word*OMEGA"])
    if "POSCON" in ftype:
        sortFeature.append(featureList["next*pos*OMEGAPOS"])
    for i in sorted(sortFeature):
            feature = feature+" "+str(i)+":1"
    vt.write(feature+'\n')
    printingFeature = feature.split()
    prevW = ""
    prevP = ""
    nextW = ""
    nextP = ""
    pos = ""
    abbr = "no"
    cap = "no"
    loc = "no"
    for i in printingFeature:
        if ":" in i:
            a = i.split(':')
            reverse = reverseList[int(a[0])].rsplit("*",1)
            abca = reverseList[int(a[0])]
            if "WORD" in ftype and "word"==reverse[0]:
                ft.write("WORD: "+ reverse[-1])
                ft.write('\n')
            if "WORDCON" in ftype and "prev*word" in reverse:
                prevW = reverse[-1]
            if "WORDCON" in ftype and "next*word" in reverse :
                nextW = reverse[-1]
            if "POSCON" in ftype and "prev*pos" in reverse:
                prevP = reverse[-1]
            if "POSCON" in ftype and "next*pos" in reverse :
                nextP = reverse[-1]
            if "POS" in ftype and "pos" in reverse:
                pos = reverse[-1]
            if "ABBR" in ftype and abca in "ABBR":
                abbr = "yes"
            if "CAP" in ftype and abca in "CAP":
                cap = "yes"
            if "LOCATION" in ftype and abca in "LOCATION":
                loc = "yes"
                    
    if iteration!=0 :    
        if "WORDCON" in ftype and prevW!="" and nextW!="":
            ft.write("WORDCON: "+prevW+" "+nextW)
            ft.write('\n')
        else :
            ft.write("WORDCON: n/a")
            ft.write('\n')
        if "POS" in ftype and pos !="":
            ft.write("POS: "+ pos)
            ft.write('\n')
        else :
            ft.write("POS: n/a")
            ft.write('\n')
        if "POSCON" in ftype and prevP!="" and nextP!="":
            ft.write("POSCON: "+prevP+" "+nextP)
            ft.write('\n')
        else :
            ft.write("POSCON: n/a")
            ft.write('\n')
        if "ABBR" in ftype and abbr!="":
            ft.write("ABBR: "+abbr)
            ft.write('\n')
        else:
            ft.write("ABBR: n/a")
            ft.write('\n')
        if "CAP" in ftype and cap!="":
            ft.write("CAP: "+cap)
            ft.write('\n')
        else:
            ft.write("CAP: n/a")
            ft.write('\n')
        if "LOCATION" in ftype and loc!="":
            ft.write("LOCATION: "+loc)
            ft.write('\n')
            ft.write('\n')
        else:
            ft.write("LOCATION: n/a")
            ft.write('\n')
            ft.write('\n')
ft.close() 
vt.close()  
