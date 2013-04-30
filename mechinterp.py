import re
from decimal import Decimal

reactions = list(range(28))
for wantreaction in reactions:
    inputfile = open('Burke-H2-2012.inp','r')
    line = inputfile.readline()
    #print(line)
    reactionsmatch = re.compile('REACTIONS')
    newlinematch = re.compile(r'\n')
    commentmatch = re.compile(r'^!')
    slashmatch = re.compile(r'/')
    lowmatch = re.compile(r'LOW')
    dupmatch = re.compile(r'DUP')
    endmatch = re.compile(r'END')
    Amatch = re.compile(r'([-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)')
    re.I
    match = reactionsmatch.search(line)
    while not match:
        line = inputfile.readline()
        match = reactionsmatch.search(line)
    print(line,end='')

    reaction = 0
    #line = inputfile.readline()

    for line in inputfile:
        skip1 = newlinematch.match(line)
        skip2 = commentmatch.match(line)
        #print(skip1, skip2)
        if not skip1 and not skip2:
            skip3 = slashmatch.search(line)
            skip4 = dupmatch.search(line)
            skip5 = endmatch.search(line)
            if not skip3 and not skip4 and not skip5:
                reaction += 1
                if reaction == wantreaction:
                    print(reaction)
                    print(line,end='')
                    Afactor = Amatch.search(line)
                    x = Decimal(Afactor.group())
                    x = 2*x               
                    modline = line[:Afactor.start()]+str(x)+line[Afactor.end():]
                    print(modline,end='')
            skip6 = lowmatch.search(line)
            if skip6 and reaction == wantreaction:
                print(line,end='')
                Afactor = Amatch.search(line)
                x = Decimal(Afactor.group())
                x = 2*x               
                modline = line[:Afactor.start()]+str(x)+line[Afactor.end():]
                print(modline,end='')
    inputfile.close()
    #print(reaction)
