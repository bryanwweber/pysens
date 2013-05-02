def mechinterp(infile, norxns):
    import re
    from decimal import Decimal

    ##norxns = 1593

    inputfile = open(infile,'r')
    lines = inputfile.readlines()
    inputfile.close()
##    outputfile = open('test.txt','w')
    reactions = [x+1 for x in range(norxns)]
    ##print(reactions)
    reactionsmatch = re.compile(r'(?i)^\bREACTIONS\b|\bREAC\b')
    newlinematch = re.compile(r'^\n')
    commentmatch = re.compile(r'^!')
    inlinecommatch = re.compile(r'.\!')
    slashmatch = re.compile(r'/')
    lowmatch = re.compile(r'(?i)^[\s]*LOW')
    highmatch = re.compile(r'(?i)^[\s]*HIGH')
    dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
    endmatch = re.compile(r'(?i)^END')
    revmatch = re.compile(r'(?i)^[\s]*REV')
    plogmatch = re.compile(r'(?i)^[\s]*PLOG')
    chebmatch = re.compile(r'(?i)^[\s]*CHEB')
    Amatch = re.compile(r'([-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)')
    re.I
    line=0
    match = reactionsmatch.search(lines[line])
    while not match:
        line+=1
        match = reactionsmatch.search(lines[line])
    ##print(line+1,lines[line],end='')
    startline = line+1
    reaction = 0
    reaclines = [0]*norxns
    #line = inputfile.readline()
    for work in lines[startline:]:
        line+=1
    ##    print(line)
        skip1 = newlinematch.search(work)
        skip2 = commentmatch.search(work)
        skip3 = slashmatch.search(work)
        skip4 = dupmatch.search(work)
        skip5 = endmatch.search(work)
        com = inlinecommatch.search(work)
        if skip3 and not skip2 and com:
    ##        print(skip3,skip2,com)
            rever = work[::-1]
    ##        print(line,rever)
            comslash = re.search(r'/(?=.*\!)(?!.*/)',rever)
            if comslash:
                skip3 = False
    ##            print(rever)
    ##        else:
    ##            print(rever)
        if not skip1 and not skip2 and not skip3 and not skip4 and not skip5:
    ##        lowline = line+1
    ##        print(reaction)
    ##        outputfile.write(str(reaction+1)+' '+work)
            reaclines[reaction] = line
            reaction += 1
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
        if skip5:
            reaclines.insert(reaction+1,line)
    ##        print(len(reaclines))
    searchlines = [0]*norxns
    extrainfo = [0]*norxns
    for lstart in range(len(reaclines)-1):
        if lstart > 2072:
            print(lstart)
        searchlines[lstart] = list(range(reaclines[lstart]+1,reaclines[lstart+1]))
    ##    print(searchlines[lstart][:])
        for lineno in searchlines[lstart][:]:
            line = lines[lineno]
    ##        print(line,end='')
            skip1 = newlinematch.match(line)
            skip2 = commentmatch.match(line)
            if not skip1 and not skip2:
    ##            print(lstart,line,end='')
                skip6 = lowmatch.search(line)
                skip7 = highmatch.search(line)
                skip8 = revmatch.search(line)
                skip9 = plogmatch.search(line)
                skip10 = chebmatch.search(line)
                if skip6:
                    extrainfo[lstart:lstart+1] = [1]
                elif skip7:
                    extrainfo[lstart:lstart+1] = [2]
                elif skip8:
                    extrainfo[lstart:lstart+1] = [3]
                elif skip9:
                    extrainfo[lstart:lstart+1] = [4]
                elif skip10:
                    extrainfo[lstart:lstart+1] = [5]
    ##                print(lstart,lineno,line,end='')
    ##print(extrainfo)
    ##for s in range(len(searchlines)):
    ##    item = str(searchlines[s])+'\n'
    ##    outputfile.write(item)
    ##for number in range(norxns):
    ##    if extrainfo[number]:
    ##        print(number,'Extra Info',extrainfo[number])

    ##print(searchlines)

    ##print(lines[reaclines[0]])      
    ##print(reaction)
##    outputfile.close()
