import re

inputfile = open('Burke-H2-2012.inp','r')
lines = inputfile.readlines()
inputfile.close()
norxns = 2072
startmatch = re.compile(r'(?i)^\bREACTIONS\b|\bREAC\b')
reactionmatch = re.compile(r'=|=>|<=>')
commentmatch = re.compile(r'^\!')

##line = 0
reaclines = [0]*norxns
reaction = 0
##match = startmatch.search(lines[line])
##while match is None:
##    line += 1
##    match = startmatch.search(lines[line])
##print(line)
for line in range(len(lines)):
    work = lines[line]
    rxn = reactionmatch.search(work)
    com = commentmatch.search(work)
    if rxn is not None and com is None:
        reaclines[reaction] = [line]
        reaction += 1
        print(reaction,work,end='')

    ##        skip6 = lowmatch.search(lines[lowline])
    ##        if skip6:
    ##            print(line,lowline)
    ##                Afactor = Amatch.search(lines[i])
    ##                x = Decimal(Afactor.group())
    ##                x = 2*x               
    ##                modline = line[:Afactor.start()]+str(x)+line[Afactor.end():]
    ##                print(modline,end='')
    ##                print(work,end='')
    ##                Afactor = Amatch.search(line)
    ##                x = Decimal(Afactor.group())
    ##                x = 2*x               
    ##                modline = line[:Afactor.start()]+str(x)+line[Afactor.end():]
    ##                print(modline,end='')
##    Amatch = re.compile(r'([-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)')
##    from decimal import Decimal
