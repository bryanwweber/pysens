
def auxcheck(lines,matchcond,rfac):
    import re
    from decimal import Decimal
    
    Amatch = re.compile(r'(([-+]?[0-9]+(\.[0-9]+)?[eE][-+]?[0-9]+)|([0]+\.?[0]+))')
    for lineNum in range(len(lines)):
        line = lines[lineNum]
        skip1 = matchcond.search(line)
        if skip1 is not None:
            Afactor = Amatch.search(line)
            x = Decimal(Afactor.group(1))
            x = rfac * x
            modline = line[:Afactor.start()] + str(x) + line[Afactor.end():]
            lines[lineNum] = modline

    return lines


class cd:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)






import re, os, subprocess, shutil
from decimal import Decimal
from mechinterp import mechinterp

commentmatch = re.compile(r'^\!') # Match exclamation points at the beginning of the string
newlinematch = re.compile(r'^\n') # Match newlines if they're the first character in the string
lowmatch = re.compile(r'(?i)^[\s]*LOW')        
highmatch = re.compile(r'(?i)^[\s]*HIGH')
dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
endmatch = re.compile(r'(?i)^END')
revmatch = re.compile(r'(?i)^[\s]*REV')
plogmatch = re.compile(r'(?i)^[\s]*PLOG')
chebmatch = re.compile(r'(?i)^[\s]*CHEB')

reactiondir = r'/home/bryan/reaction/chemkin15113_linuxx8664/'

inputfile = open('chem.inp','r')
lines = inputfile.readlines()
inputfile.close()

numRxns = 2072
rfactor = 1
wantreaction = [1]#[x+1 for x in range(1920,numRxns)]
ignSens = [0]*len(wantreaction)
reacLines, searchLines, extraInfo = mechinterp(lines,numRxns)
tignsens = open('tignsens.csv','a',0)
Amatch = re.compile(r'([-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)')
for i in range(len(wantreaction)):
    rxnNum = wantreaction[i]-1
    outLines = lines[:]
    line = lines[reacLines[rxnNum]]
    Afactor = Amatch.search(line)
##    print(rxnNum, Afactor.group(1))
    x = Decimal(Afactor.group(1))
    x = rfactor*x
    modline = line[:Afactor.start()] + str(x) + line[Afactor.end():]
    outLines[reacLines[rxnNum]] = modline
    if extraInfo[rxnNum] > 0:
        sendLines = [0]*len(searchLines[rxnNum])
        for n in range(len(searchLines[rxnNum])):
            sendLines[n] = lines[searchLines[rxnNum][n]]
        
        if extraInfo[rxnNum] == 1:
            tr = auxcheck(sendLines,lowmatch,rfactor)
        elif extraInfo[rxnNum] == 2:
            tr = auxcheck(sendLines,highmatch,rfactor)
        elif extraInfo[rxnNum] == 3:
            tr = auxcheck(sendLines,revmatch,rfactor)
        elif extraInfo[rxnNum] == 4:
            tr = auxcheck(sendLines,plogmatch,rfactor)
        elif extraInfo[rxnNum] == 5:
            tr = auxcheck(sendLines,lowmatch,rfactor)
##            
        for n in range(len(searchLines[rxnNum])):
            outLines[searchLines[rxnNum][n]] = tr[n]
    chemfolder = 'Reaction'+str(rxnNum+1)
    if not os.path.exists(chemfolder):
        os.makedirs(chemfolder)
    shutil.copyfile('test.inp',chemfolder+'/test.inp')
    shutil.copyfile('CKSolnList.txt',chemfolder+'/CKSolnList.txt')
    shutil.copyfile(reactiondir+'data/chemkindata.dtd',chemfolder+'/chemkindata.dtd')
    shutil.copyfile('therm.dat',chemfolder+'/therm.dat')
    inpfile = r'test.inp'
    outfile = r'test.out'
    reactor = reactiondir + r'bin/CKReactorGenericClosed'
    ckinterp = reactiondir + r'bin/chem'
    chemoutput = 'chem.out'
    chemasc = 'chem.asc'
    with cd(chemfolder):    
        chemfilename = 'chem'+str(rxnNum+1)+'.inp'
        chemfile = open(chemfilename,'w')
        for line in outLines:
            chemfile.write(line)
        chemfile.close()
        subprocess.call([ckinterp,'-i',chemfilename,'-o',chemoutput,'-d','therm.dat','-c',chemasc])
        subprocess.call([reactor,'-i',inpfile,'-o',outfile,'Pro','-c','chem.asc'])
        subprocess.call(['GetSolution','CKSolnList.txt','XMLdata.zip'])
        subprocess.call(['CKSolnTranspose'])
        outputFile = open('CKSoln_solution_point_value_vs_solution_number.csv','r')
        ignLines = outputFile.readlines()
        ignDelay = Decimal([x.strip() for x in ignLines[1].split(',')][-1])
        ignSens= [rxnNum+1,rfactor,ignDelay]
        printsens = ','.join(map(str,ignSens))
        tignsens.write(printsens+'\n')
    
    shutil.rmtree(chemfolder)
    print(rxnNum+1,ignDelay)
tignsens.close()
