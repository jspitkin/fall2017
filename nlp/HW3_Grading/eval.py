# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 17:56:46 2017

@author: Raghubar
"""

import sys

predict = sys.argv[1]
gold = sys.argv[2]
predictData = []
fileRead = open(predict)
for row in fileRead:
    predictData += row.strip('\n').split('\r')
goldData = []
fileRead = open(gold)
for row in fileRead:
    goldData += row.strip('\n').split('\r')


def add(ext, DT, added, start, end):
    if len(ext) > 0 : 
        pDict = []
        pDict.append(start)
        pDict.append(end)
        if added :
            if ext not in DT :
                DT[ext] = []
            DT[ext].append(pDict)
personPredictData = {}
locPredictData = {}
orgPredictData = {}
ext = ""
start = 0
end = 0
p = False
l = False
o = False
for i in range(len(predictData)) :
    wds = predictData[i].split()
    if wds[0].startswith("B-") :
        
        add(ext, personPredictData, p, start, end)    
        add(ext, locPredictData, l, start, end)
        add(ext, orgPredictData, o, start, end)
        start = i + 1
        end = i + 1
        ext = wds[1]
        p = False
        l = False
        o = False
        if wds[0].endswith("PER") :
            p = True
        elif wds[0].endswith("LOC") :
            l = True
        elif wds[0].endswith("ORG") :
            o = True
    elif wds[0].startswith("I-") :
        if (wds[0].endswith("PER") and p) or (wds[0].endswith("LOC") and l) or (wds[0].endswith("ORG") and o):
            ext += " " + wds[1]
            end = i + 1
        else :
            add(ext, personPredictData, p, start, end)    
            add(ext, locPredictData, l, start, end)
            add(ext, orgPredictData, o, start, end)
            p = False
            l = False
            o = False
            ext = ""
    else :
        add(ext, personPredictData, p, start, end)    
        add(ext, locPredictData, l, start, end)
        add(ext, orgPredictData, o, start, end)
        p = False
        l = False
        o = False
        ext = ""
add(ext, personPredictData, p, start, end)    
add(ext, locPredictData, l, start, end)
add(ext, orgPredictData, o, start, end)


personGoldData = {}
locGoldData = {}
orgGoldData = {}
ext = ""
start = 0
end = 0
p = False
l = False
o = False
for i in range(len(goldData)) :
    wds = goldData[i].split()
    if wds[0].startswith("B-") :
        add(ext, personGoldData, p, start, end)    
        add(ext, locGoldData, l, start, end)
        add(ext, orgGoldData, o, start, end)
        start = i + 1
        end = i + 1
        ext = wds[1]
        p = False
        l = False
        o = False
        if wds[0].endswith("PER") :
            p = True
        elif wds[0].endswith("LOC") :
            l = True
        elif wds[0].endswith("ORG") :
            o = True
    elif wds[0].startswith("I-") :
        if (wds[0].endswith("PER") and p) or (wds[0].endswith("LOC") and l) or (wds[0].endswith("ORG") and o):
            ext += " " + wds[1]
            end = i + 1
        else :
            add(ext, personGoldData, p, start, end)    
            add(ext, locGoldData, l, start, end)
            add(ext, orgGoldData, o, start, end)
            p = False
            l = False
            o = False
            ext = ""
    else :
        add(ext, personGoldData, p, start, end)    
        add(ext, locGoldData, l, start, end)
        add(ext, orgGoldData, o, start, end)
        p = False
        l = False
        o = False
        ext = ""
add(ext, personGoldData, p, start, end)    
add(ext, locGoldData, l, start, end)
add(ext, orgGoldData, o, start, end)
display = []
cPER = 0
pPER = 0
gPER = 0
strg = ""
dicty = {}
for key in personPredictData :
    pPOS = personPredictData[key]
    if key in personGoldData :
        gPOS = personGoldData[key]
        for x in pPOS :
            for y in gPOS :
                if x[0] == y[0] and x[1] == y[1] :
                    cPER += 1
                    dicty[x[0]] = key + "[" + str(x[0]) + "-" + str(x[1]) + "]" 
    pPER += len(pPOS) 
for key in personGoldData :
    gPER += len(personGoldData[key])
for key in sorted(dicty) :
    strg += dicty[key] + " | "
strg = strg.rstrip(" | ").strip()
if(len(strg) < 1) :
    strg = "NONE"
display.append("Correct PER = " + strg)
if gPER > 0 :
    display.append("Recall PER = " + str(cPER) + "/" + str(gPER))
else :
    display.append("Recall PER = n/a")
if pPER > 0 :
    display.append("Precision PER = " + str(cPER) + "/" + str(pPER))
else :
    display.append("Precision PER = n/a")

cLOC = 0
pLOC = 0
gLOC = 0
strg = ""
dicty = {}
for key in locPredictData :
    pPOS = locPredictData[key]
    if key in locGoldData :
        gPOS = locGoldData[key]
        for x in pPOS :
            for y in gPOS :
                if x[0] == y[0] and x[1] == y[1] :
                    cLOC += 1
                    dicty[x[0]] = key + "[" + str(x[0]) + "-" + str(x[1]) + "]" 
    pLOC += len(pPOS) 
for key in locGoldData :
    gLOC += len(locGoldData[key])
for key in sorted(dicty) :
    strg += dicty[key] + " | "
strg = strg.rstrip(" | ").strip()
if(len(strg) < 1) :
    strg = "NONE"
display.append("Correct LOC = " + strg)
if gLOC > 0 :
    display.append("Recall LOC = " + str(cLOC) + "/" + str(gLOC))
else :
    display.append("Recall LOC = n/a")
if pLOC > 0 :
    display.append("Precision LOC = " + str(cLOC) + "/" + str(pLOC))
else :
    display.append("Precision LOC = n/a")
    
cORG = 0
pORG = 0
gORG = 0
strg = ""
dicty = {}
for key in orgPredictData :
    pPOS = orgPredictData[key]
    if key in orgGoldData :
        gPOS = orgGoldData[key]
        for x in pPOS :
            for y in gPOS :
                if x[0] == y[0] and x[1] == y[1] :
                    cLOC += 1
                    dicty[x[0]] = key + "[" + str(x[0]) + "-" + str(x[1]) + "]" 
    pORG += len(pPOS) 
for key in orgGoldData :
    gLOC += len(orgGoldData[key])
    gORG += len(orgGoldData[key])
    strg += dicty[key] + " | "
strg = strg.rstrip(" | ").strip()
if(len(strg) < 1) :
    strg = "NONE"
display.append("Correct ORG = " + strg)
if gORG > 0 :
    display.append("Recall ORG = " + str(cORG) + "/" + str(gORG))
else :
    display.append("Recall ORG = n/a")
if pORG > 0 :
    display.append("Precision ORG = " + str(cORG) + "/" + str(pORG))
else :
    display.append("Precision ORG = n/a")

f = open("trace-eval.txt", "w+")
for i in range(len(display)) :
    f.write(display[i] + "\n")
    if (i + 1) % 3 == 0 :
        f.write("\n")    
if (gPER + gLOC + gORG) > 0 :
    f.write("Average Recall = " + str((cPER + cLOC + cORG)) + "/" + str((gPER + gLOC + gORG)) + "\n")
else :
    f.write("Average Recall = n/a\n")
if (pPER + pLOC + pORG) > 0 :
    f.write("Average Precision = " + str((cPER + cLOC + cORG)) + "/" + str((pPER + pLOC + pORG)) + "\n")
else :
    f.write("Average Precision = n/a\n")
f.close()
