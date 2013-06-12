import re
from mechinterp import mechinterp

chem = open('Burke-H2-2012.inp','r')
lines = chem.readlines()
chem.close()

numRxns = 27
rxnLines = mechinterp(lines,numRxns)[0]
specNum = []
startSpec = 'H2'
specmatch = re.compile(r'\b'+startSpec+r'\b')
reacmatch = re.compile(r'((^|^[\s]+)[\s\w\d\(\)+=<>-_*]+(\s))')
prodsplit = re.compile(r'[\s]*=|=>|<=>[\s]*')
specsplit = re.compile(r'[\s(]*\+|=|=>|<=>[\s]*')
sidesplit = re.compile(r'[(\s]*\+[\s]*')
reacList = []
leftSide = []
rightSide = []
species = []
for i in range(len(rxnLines)-1):
    reacList.append(reacmatch.search(lines[rxnLines[i]]).group(1).strip())
    leftSide.append(prodsplit.split(reacList[i])[0].strip())
    rightSide.append(prodsplit.split(reacList[i])[1].strip())
    spec = specsplit.split(reacList[i])
    for s in spec:
        if s.strip('() ').lower() != 'm':
            species.append(s.strip())

species = list(set(species))
##for i in species[:]:
##    if 'M' in i:
##        species.remove(i)
print(species)
adj = []
adjacency = [0]*len(species)
for i in range(len(reacList)):
    if specmatch.search(leftSide[i]) is not None:
##        print('In Left Side',i+1)
        spec = sidesplit.split(rightSide[i])
        leftSide[i] = ''
        rightSide[i] = ''
        for s in spec:
            if s.strip('() ').lower() != 'm':
                adj.append(s.strip())
    elif specmatch.search(rightSide[i]) is not None:
        spec = sidesplit.split(leftSide[i])
        leftSide[i] = ''
        rightSide[i] = ''
        for s in spec:
            if s.strip('() ').lower() != 'm':
                adj.append(s.strip())
    adj = list(set(adj))
adjacency[0] = adj
adj = []
for i in range(len(reacList)):
print(adjacency)
