###############################################################################
#
#Begin driver script for running the sensitivity analysis
#
#
#Import the necessary modules, including mechinterp from mechinterp.py and all
#of the modules from sens_helper.
#
import re, os, subprocess, shutil
from itertools import product
from decimal import *
from mechinterp import mechinterp
from sens_helper import *

###############################################################################
#These are the user input variables. The user should change each of them to   
#match their mechanism. `inputfilename` is the original chemistry file.       
#`thermfile` is the file containing the thermo data, if necessary. If the     
#thermo data is included in the chemistry input file, this variable will not  
#be used. `numRxns` is the number of reactions in the mechanism. `rfactor` is 
#the multiplication factor for each reaction. `wantreaction` is a list of the 
#reaction numbers the user wishes to be analyzed. `sensfilename` is the       
#filename in which the comma-seperated output should be stored. `siminputfile`
#is the file name of the file storing input information for the simulation.   
#                                                                             
inputfilename = 'Burke-H2-2012.inp'
thermfile = ''
numRxns = 28
rfactors = ['1']
wantreactions = [4]#[x+1 for x in range(1920,numRxns)]
sensfilename = 'tignsens.csv'
siminputfiles = ['test.inp']
#                                                                             
###############################################################################

#
#Compile the required regular expressions
#
commentmatch = re.compile(r'^\!')
newlinematch = re.compile(r'^\n')
#
#The following regular expressions match the keywords we expect to see.
#The `(?i)` indicates case insensitive. For certain keywords, we want to
#match the keyword even if there is space at the beginning of the line;
#these keywords have `^[\s]*`.
#
lowmatch = re.compile(r'(?i)^[\s]*LOW')
highmatch = re.compile(r'(?i)^[\s]*HIGH')
dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
endmatch = re.compile(r'(?i)^END')
revmatch = re.compile(r'(?i)^[\s]*REV')
plogmatch = re.compile(r'(?i)^[\s]*PLOG')
Amatch = re.compile(r'((?<![\w\-])([-+]?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?)(?!\w))')
reacmatch = re.compile(r'((^|^[\s]+)[\s\w\d\(\)+=<>-_*]+(\s))')
#
#Set the directory of the current version of CHEMKIN-Pro
#
reactiondir = r'/home/bryan/reaction/chemkin15113_linuxx8664/'
#
#Set the location of the binary files.
#
reactor = reactiondir + r'bin/CKReactorGenericClosed'
ckinterp = reactiondir + r'bin/chem'
#
#Open, read, and close the input file. The lines of the input file are
#stored in the list `lines`. 
#
with open(inputfilename,'r') as inputfile:
    lines = inputfile.readlines()
##tignsens = open('tignsens.csv','a',0)
#
#Call the mechanism interpreter module. The mechinterp function returns
#a tuple of lists plus a boolean. The lists contain the line numbers in
#the input file of the reactions, the lines between each reaction, and
# whether a reaction has auxiliary information. The boolean checks
#whether the thermo data is available in the chemistry file or if it
#should be taken from a separate file. These are stored, respectively,
# in `reacLines`, `searchLines`, `extraInfo` and `thermInChem`.
#
reacLines, searchLines, extraInfo, thermInChem = mechinterp(lines,numRxns)
#
#Set filenames of simulation output files.
#
outfile = r'test.out'
chemoutput = r'chem.out'
chemasc = r'chem.asc'
totalCase = len(wantreactions)*len(siminputfiles)*len(rfactors)
for j,(inpfile,rfactor) in enumerate(product(siminputfiles,rfactors)):
    csvoutput = 'tignsens_' + inpfile.strip('.inp') + '_' + rfactor + 'x.csv'
    with open(csvoutput,'a',0) as tignsens:
        #
        #Loop through the reaction numbers in `wantreactions`. `i` is our loop
        #variable.
        #
        for i,wantreaction in enumerate(wantreactions):
            #
            #Python is zero-based, so we have to subtract 1 from the numbers in
            #`wantreaction` to properly find the index of the other lists
            #
            rxnNum = wantreaction-1
            #
            #outLines is the list of lines to write to the chem.inp file to
            #be run in the simulation. It needs to be reset on every loop or
            #more than one reaction will be modified at a time. Python is
            #pointer-based, so we have to set `outLines` equal to a slice of
            #`lines`, the input list of lines (the slice happens to be the whole
            #list).
            #
            outLines = lines[:]
            #
            #Grab the line from the input file that matches the reaction were
            #working on
            #
            line = lines[reacLines[rxnNum]]
            #
            #Find the Arrhenius coefficient on this line
            #
            Afactor = Amatch.search(line)
            #
            #Set `x` to the arbitrary precision conversion of the first matching
            #string from the Afactor match. Multiply `x` by `rfactor`.
            #Reassemble the modified reaction line with the new Arrhenius
            #coefficient, and set the correct line in `outLines` to the modified
            #line.
            #
            x = Decimal(Afactor.group(1))
            x = Decimal(rfactor)*x
            modline = line[:Afactor.start()] + str(x) + line[Afactor.end():]
            outLines[reacLines[rxnNum]] = modline
            #
            #Check if there is auxiliary information for the current reaction
            #
            if extraInfo[rxnNum] > 0:
                #
                #If there is auxiliary information, initialize a list for input
                #lines that will be sent for modification. Then loop through the
                #lines in the searchLines list for the correct reaction number
                #and construct the list to send for modification.
                #
                sendLines = [0]*len(searchLines[rxnNum])
                for n in range(len(searchLines[rxnNum])):
                    sendLines[n] = lines[searchLines[rxnNum][n]]
                #
                #If structure to check which type of auxiliary information is
                #present and send the proper compiled regular expression to
                #auxcheck. `ret` is the returned list of modified lines.
                #
                if extraInfo[rxnNum] == 1:
                    ret = auxcheck(sendLines,lowmatch,rfactor)
                elif extraInfo[rxnNum] == 2:
                    ret = auxcheck(sendLines,highmatch,rfactor)
                elif extraInfo[rxnNum] == 3:
                    ret = auxcheck(sendLines,revmatch,rfactor)
                elif extraInfo[rxnNum] == 4:
                    ret = auxcheck(sendLines,plogmatch,rfactor)
                elif extraInfo[rxnNum] == 5:
                    ret = chebcheck(sendLines,rfactor)
                #
                #Loop through the returned lines and set the correct line in the
                #`outLines` list to the modified lines.
                #
                for n in range(len(searchLines[rxnNum])):
                    outLines[searchLines[rxnNum][n]] = ret[n]
                #
                #Done checking auxiliary information
                #
            #
            #Create a folder in which simulations will be run, after checking
            #for its existence.
            #
            chemfolder = 'Reaction' + str(rxnNum + 1)
            if not os.path.exists(chemfolder):
                os.makedirs(chemfolder)
            #
            #Copy the various files we will need to run the simulation into the
            #simulation directory.
            #
            shutil.copyfile(inpfile, chemfolder + '/' + inpfile)
            shutil.copyfile('CKSolnList.txt', chemfolder + '/CKSolnList.txt')
            shutil.copyfile(reactiondir + 'data/chemkindata.dtd',
                            chemfolder + '/chemkindata.dtd')
            #
            #If the thermo data is in the chemistry file, we don't have to copy
            #therm.dat
            if not thermInChem:
                shutil.copyfile(thermfile, chemfolder + '/' + thermfile)
            #
            #Change directory into the simulation directory.
            #
            with cd(chemfolder):
                #
                #Set the filename for the modified chemistry input file. Open
                #the modified chemistry input file with write access, and write
                #the file. This write is buffered. Close the modified chemistry
                #input file.
                #
                chemfilename = 'chem' + str(rxnNum + 1) + '.inp'
                with open(chemfilename, 'w') as chemfile:
                    for outLine in outLines:
                        chemfile.write(outLine)
                #
                #Call the CHEMKIN-Pro interpreter, then the solver, then the
                #post-processor, then the transpose utility to create the
                #solution .csv files. First check if we need the thermo file.
                #
                if thermInChem:
                    subprocess.call([ckinterp, '-i', chemfilename, '-o', chemoutput,
                                     '-c', chemasc])
                else:
                    subprocess.call([ckinterp, '-i', chemfilename, '-o', chemoutput,
                                     '-d', thermfile, '-c', chemasc])
                #
                #End if
                #
                subprocess.call([reactor, '-i',inpfile, '-o', outfile,
                                 'Pro', '-c', chemasc])
                subprocess.call(['GetSolution', 'CKSolnList.txt', 'XMLdata.zip'])
                subprocess.call(['CKSolnTranspose'])
                #
                #Open, read, and close the file with the solution information.
                #
                with open('CKSoln_solution_point_value_vs_solution_number.csv',
                                  'r') as outputFile:
                    ignLines = outputFile.readlines()
                #
                #We are interested in the last column on the second line of the
                #output file. This contains the ignition delay if the simulation
                #ignited. If not, it will have a 1000/T, which should be
                #different from a typical ignition delay so we can find it in
                #the final output. Convert the ignition delay to an arbitrary
                #precision number.
                #
                ignCol = [x for x,val in enumerate(ignLines[0].split(',')) if 'Ignition' in val]
                ignDelay = [float(k) for k in [ignLines[1].split(',')[x].strip() for x in ignCol]]
                #
                #Create a list for writing to the output file, including the
                #corrected (i.e. one-based) reaction number, the multiplication
                #factor, and the ignition delay. Format the list into a comma-
                #separated format and convert to a string. Then append a newline
                #and print the list to the sensitivity output file.
                #
                ignSens = [rxnNum + 1, rfactor,'','',reacmatch.search(line).group(1).strip()]
                ignSens[2:2] = ignDelay
                printsens = ','.join(map(str, ignSens))
                tignsens.write(printsens + '\n')
                #
                #Done in the `chemfolder` directory.
                #
            #
            #Remove the simulation directory.
            #
            #shutil.rmtree(chemfolder)
            #
            #Print to the screen some progress information.
            #
            caseNo = i+1 + j*len(wantreactions)
            print('Case {0} of {1} \nReaction #: {2} \nIgnition Delay: {3}\nTemperature: {4}\nFactor: {5}'
                  .format(caseNo,totalCase,rxnNum+1,ignDelay,inpfile,rfactor))
            #
            #Done with the loop through `wantreactions`.
            #

#
#END
#
###############################################################################
