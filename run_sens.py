###############################################################################
def auxcheck(lines,matchcond,rfac):
    """Take auxiliary lines and return lines with modified Arrhenius coefficients.

    INPUT:
    lines - list of auxiliary information lines to check
    matchcond - compiled regular expression used to search the auxiliary
                lines for a particular condition
    rfac - multiplication factor for the Arrhenius coefficients
    OUTPUT:
    lines - list of modified auxiliary information lines

    """
#
#Begin function
#
    #
    #Import the module for regular expressions and for converting
    #strings to arbitrary precision numbers
    #
    import re
    from decimal import Decimal
    #
    #Compile the regular expression to match the Arrhenius coefficients
    #
    Amatch = re.compile(r'(([-+]?[0-9]+(\.[0-9]+)?[eE][-+]?[0-9]+)|([0]+\.?[0]+))')
    #
    #Loop through the lines in the input list
    #
    for lineNum in range(len(lines)):
        line = lines[lineNum]
        #
        #Check that the line matches the input matching condition. If
        #not, the line is not modified
        #
        skip1 = matchcond.search(line)
        if skip1 is not None:
            #
            #If the line matches the proper condition, find the
            #Arrhenius coefficient, multiply it by two, reconstruct
            #the line, and overwrite the original line in the input
            #list.
            Afactor = Amatch.search(line)
            x = Decimal(Afactor.group(1))
            x = rfac * x
            modline = line[:Afactor.start()] + str(x) + line[Afactor.end():]
            lines[lineNum] = modline
    #
    #Return the list of modified lines
    #
    return lines
###############################################################################
###############################################################################
class cd:

    """Change directory.

    For use with the `with` keyword, i.e. `with cd(dir)` changes to the
    directory `dir`
    
    """
    
    def __init__(self, newPath):
        """Set the newPath attribute to be the argument passed to the class."""
        self.newPath = newPath

    def __enter__(self):
        """Change directory when the class is entered."""
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        """Change back when the class is exited"""
        os.chdir(self.savedPath)
###############################################################################
###############################################################################
#
#Begin driver script for running the sensitivity analysis
#
#
#Import the necessary modules, including mechinterp from mechinterp.py
#
import re, os, subprocess, shutil
from decimal import Decimal
from mechinterp import mechinterp

###############################################################################
#These are the user input variables. The user should change each of them to   #
#match their mechanism. `inputfilename` is the original chemistry file.       #
#`numRxns` is the number of reactions in the mechanism. `rfactor` is the      #
#multiplication factor for each reaction. `wantreaction` is a list of the     #
#reaction numbers the user wishes to be analyzed. `sensfilename` is the       #
#filename in which the comma-seperated output should be stored. `siminputfile`#
#is the file name of the file storing input information for the simulation.   #
#                                                                             #
inputfilename = 'chem.inp'                                                    #
numRxns = 2072                                                                #
rfactor = 1                                                                   #
wantreaction = [1]#[x+1 for x in range(1920,numRxns)]                         #
sensfilename = 'tignsens.csv'                                                 #
siminputfile = 'test.inp'                                                     #
#                                                                             #
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
chebmatch = re.compile(r'(?i)^[\s]*CHEB')
Amatch = re.compile(r'([-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)')
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
#stored in the list `lines`. Also open the output file with append
#access. Set the buffer of the output file to be zero lines because
#problems have been encountered with fully buffered writes. This may
#have something to do with the buffered write of the chemistry input
#file.
#
inputfile = open(inputfilename,'r')
lines = inputfile.readlines()
inputfile.close()
tignsens = open('tignsens.csv','a',0)
#
#Call the mechanism interpreter module. The mechinterp function returns
#a tuple of lists - the line numbers in the input file of the reactions,
#the lines between each reaction, and whether a reaction has auxiliary
#information. These are stored, respectively, in `reacLines`,
#`searchLines`, and `extraInfo`.
#
reacLines, searchLines, extraInfo = mechinterp(lines,numRxns)
#
#Set filenames of simulation input and output files.
#
inpfile = r'test.inp'
outfile = r'test.out'
chemoutput = r'chem.out'
chemasc = r'chem.asc'
thermfile = r'therm.dat'
#
#Loop through the reaction numbers in `wantreaction`. `i` is our loop
#variable.
#
for i in range(len(wantreaction)):
    #
    #Python is zero-based, so we have to subtract 1 from the numbers in
    #`wantreaction` to properly find the index of the other lists
    #
    rxnNum = wantreaction[i]-1
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
    x = rfactor*x
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
            #
            #CHEB reactions aren't implemented yet, so send a match
            #condition that won't match any lines.
            #
            ret = auxcheck(sendLines,lowmatch,rfactor)
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
    shutil.copyfile(siminputfile, chemfolder + '/' + inpfile)
    shutil.copyfile('CKSolnList.txt', chemfolder + '/CKSolnList.txt')
    shutil.copyfile(reactiondir + 'data/chemkindata.dtd',
                    chemfolder + '/chemkindata.dtd')
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
        chemfile = open(chemfilename, 'w')
        for line in outLines:
            chemfile.write(line)
        chemfile.close()
        #
        #Call the CHEMKIN-Pro interpreter, then the solver, then the
        #post-processor, then the transpose utility to create the
        #solution .csv files.
        #
        subprocess.call([ckinterp, '-i', chemfilename, '-o', chemoutput,
                         '-d', thermfile, '-c', chemasc])
        subprocess.call([reactor, '-i',inpfile, '-o', outfile,
                         'Pro', '-c', chemasc])
        subprocess.call(['GetSolution', 'CKSolnList.txt', 'XMLdata.zip'])
        subprocess.call(['CKSolnTranspose'])
        #
        #Open, read, and close the file with the solution information.
        #
        outputFile = open('CKSoln_solution_point_value_vs_solution_number.csv',
                          'r')
        ignLines = outputFile.readlines()
        outputFile.close()
        #
        #We are interested in the last column on the second line of the
        #output file. This contains the ignition delay if the simulation
        #ignited. If not, it will have a 1000/T, which should be
        #different from a typical ignition delay so we can find it in
        #the final output. Convert the ignition delay to an arbitrary
        #precision number.
        #
        ignDelay = Decimal([x.strip() for x in ignLines[1].split(',')][-1])
        #
        #Create a list for writing to the output file, including the
        #corrected (i.e. one-based) reaction number, the multiplication
        #factor, and the ignition delay. Format the list into a comma-
        #separated format and convert to a string. Then append a newline
        #and print the list to the sensitivity output file.
        #
        ignSens= [rxnNum + 1, rfactor, ignDelay]
        printsens = ','.join(map(str, ignSens))
        tignsens.write(printsens + '\n')
        #
        #Done in the `chemfolder` directory.
        #
    #
    #Remove the simulation directory.
    #
    shutil.rmtree(chemfolder)
    #
    #Print to the screen some progress information.
    #
    print(i+1, 'of', len(wantreaction), rxnNum + 1, ignDelay)
    #
    #Done with the loop through `wantreaction`.
    #
#
#Close the sensitivity output file.
#
tignsens.close()
#
#END
#
###############################################################################
