#! /usr/bin/python3 -u

# System imports
import re
import os
import subprocess
import shutil
import sys
from itertools import product
from decimal import *

# Local imports
from mechinterp import mechinterp
from sens_helper import *


def main():
    # Read the configuration file.
    config = NoSectionConfigParser()
    config.read('pysens.conf')
    default = config['DEFAULT']

    # Set the location of the CHEMKIN executable files. Expand any shell
    # variables in the input.
    reactiondir = default['chemkin root']
    if '$' in reactiondir:
        reactiondir = os.path.expandvars(reactiondir)
        if os.path.isdir(reactiondir):
            reactor = os.path.join(reactiondir, 'bin', 'CKReactorGenericClosed')
            ckinterp = os.path.join(reactiondir, 'bin', 'chem')
            if not os.path.isfile(reactor) or not os.path.isfile(ckinterp):
                print("Error: The reactor and CHEMKIN interpreter must "
                      "exist at CHEMKIN_ROOT/bin/")
                sys.exit(1)
        else:
            print("Error: The proper path to the CHEMKIN root "
                  "directory must be specified")
            sys.exit(1)

    # Set the mechanism to be used.
    if ('mech input file' in default and
            os.path.isfile(default['mech input file'])):
        inputfilename = default['mech input file']
    else:
        print("Error: the mechanism file must be specified in the "
              "configuration file, and it must exist")
        sys.exit(1)

    # Set the simulation input file to be used.
    if 'sim input files' in default:
        siminputfiles = [x.strip() for x in
                         default['sim input files'].split(',')
                         ]
        for fname in siminputfiles:
            if not os.path.isfile(fname):
                print("Error: the specified input file {} does not "
                      "exist".format(fname))
                sys.exit(1)
    else:
        print("Error: the simulation input file must be specified in "
              "the configuration file")
        sys.exit(1)

    # Set the multiplication factors to be used.
    if 'factors' in default:
        multfactors = [x.strip for x in default['factors'].split(',')]
    else:
        print("Error: at least one multiplication factor must be "
              "specified in the configuration file")
        sys.exit(1)

    # Set the base of the csv output file name.
    if 'outputfile' in default:
        sensfilenamebase = default['outputfile']
    else:
        print("Error: the base of the csv output filename must be "
              "specified in the configuration file")
        sys.exit(1)

    # Compile the required regular expressions
    commentmatch = re.compile(r'^\!')
    newlinematch = re.compile(r'^\n')

    # The following regular expressions match the keywords we expect to
    # see. The `(?i)` indicates case insensitive. For certain keywords,
    # we want to match the keyword even if there is space at the
    # beginning of the line; these keywords have `^[\s]*`.
    lowmatch = re.compile(r'(?i)^[\s]*LOW')
    highmatch = re.compile(r'(?i)^[\s]*HIGH')
    dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
    endmatch = re.compile(r'(?i)^END')
    revmatch = re.compile(r'(?i)^[\s]*REV')
    plogmatch = re.compile(r'(?i)^[\s]*PLOG')
    Amatch = re.compile(r'((?<![\w\-\()])([-+]?[0-9]+(\.[0-9]+)?'
                        '([eE][-+]?[0-9]+)?)(?!\w))'
                        )
    reacmatch = re.compile(r'((^|^[\s]+)[\s\w\d()+=<>\- *.]+?(?=\s\d))')

    # Open, read, and close the input file. The lines of the input file
    # are stored in the list `lines`.
    try:
        with open(inputfilename, 'rt') as inputfile:
            lines = inputfile.readlines()
    except UnicodeDecodeError:
        with open(inputfilename, 'rt', encoding='latin-1') as inputfile:
            lines = inputfile.readlines()

    # Call the mechanism interpreter module. The mechinterp function
    # returns a tuple of lists plus a boolean. The lists contain the
    # line numbers in the input file of the reactions, the lines between
    # each reaction, and whether a reaction has auxiliary information.
    # The boolean checks whether the thermo data is available in the
    # chemistry file or if it should be taken from a separate file.
    # These are stored, respectively, in `reacLines`, `searchLines`,
    # `extraInfo` and `thermInChem`.
    reacLines, searchLines, extraInfo, thermInChem, = mechinterp(lines)

    # Set the thermo file, if necessary.
    if (not thermInChem and 'thermo input file' in default and
            os.path.isfile(default['thermo input file'])):
        thermfilename = default['thermo input file']
    elif (not thermInChem and ('thermo input file' not in default or not
            os.path.isfile(default['thermo input file']))):
        print("Error: the thermo file must be specified in the "
              "configuration file, and it must exist")
        sys.exit(1)

    # Set the reactions we want to work with.
    numRxns = len(reacLines)-1
    if 'reactions' not in default:
        print("Error: the reactions to study must be specified in the "
              "configuration file")
        sys.exit(1)
    else:
        wantrxns = default['reactions']

    if wantrxns == 'all':
        wantreactions = [x + 1 for x in range(numRxns)]
        print("All {} reactions are considered in these "
              "analyses".format(numRxns))
    elif ',' in wantrxns and ':' in wantrxns:
        print("Error: use one of commas or colons to separate the wanted "
              "reactions")
        sys.exit(1)
    elif ',' in wantrxns:
        wantreactions = [int(number) for number in wantrxns.split(',') if
            number]
        print("The reactions considered in these analyses are "
              "{}".format(wantreactions))
    elif ':' in wantrxns:
        if wantrxns.endswith(':') or wantrxns.endswith('end'):
            spl = list(map(int, wantrxns.split(':')[:-1]))
            spl.append(numRxns)
        else:
            spl = list(map(int, wantrxns.split(':')))

        if len(spl) == 2:
            wantreactions = list(range(spl[0], spl[1] + 1))
        elif len(spl) == 3:
            if spl[1] >= 1:
                wantreactions = list(range(spl[0], spl[2] + 1, spl[1]))
            else:
                print("Error: the interval in the reactions specification "
                      "must be >= 1")
                sys.exit(1)
        else:
            print("Error: Specify either start:stop or start:interval:stop "
                  "for reactions")
            sys.exit(1)
        print("The reactions considered in these analyses are "
              "{}".format(wantreactions))
    else:
        wantreactions = list(int(wantrxns))
        print("The reaction considered in these analyses is "
              "{}".format(wantreactions))

    # Set filenames of simulation and output files.
    simoutputfile = 'test.out'
    chemoutput = 'chem.out'
    chemasc = 'chem.asc'
    totalCases = len(wantreactions)*len(siminputfiles)*len(multfactors)
    for j, (inpfile, multfactor) in enumerate(product(siminputfiles, multfactors)):
        csvoutput = (sensfilenamebase + '_' + inpfile.rstrip('.inp') + '_' +
            multfactor + 'x.csv')
        with open(csvoutput, 'at') as tignsens:

            # Loop through the reaction numbers in `wantreaction`. `i`
            # is the loop variable.
            for i, wantreaction in enumerate(wantreactions):

                # Python is zero-based, so we have to subtract 1 from
                # the numbers in `wantreaction` to properly find the
                # index of the other lists
                rxnNum = wantreaction - 1

                # outLines is the list of lines to write to the chem.inp
                # file to be run in the simulation. It needs to be reset
                # on every loop or more than one reaction will be
                # modified at a time. Python is "pointer-based", so we
                # have to set `outLines` equal to a slice of `lines`,
                # the input list of lines (the slice happens to be the
                # whole list).
                outLines = lines[:]

                # Grab the line from the input file that matches the
                # reaction we're working on.
                line = lines[reacLines[rxnNum]]

                # Find the Arrhenius coefficient on this line.
                Afactor = Amatch.search(line)

                # Set `x` to the arbitrary precision conversion of the
                # first matching string from the Afactor match. Multiply
                # `x` by `multfactor`. Reassemble the modified reaction
                # line with the new Arrhenius coefficient, and set the
                # correct line in `outLines` to the modified line.
                x = Decimal(Afactor.group(1))
                x = Decimal(multfactor)*x
                modline = (line[:Afactor.start()] + str(x) +
                    line[Afactor.end():])
                outLines[reacLines[rxnNum]] = modline

                # Check if there is auxiliary information for the
                # current reaction.
                if extraInfo[rxnNum] > 0:

                    # If there is auxiliary information, initialize a
                    # list for input lines that will be sent for
                    # modification. Then loop through the lines in the
                    # searchLines list for the correct reaction number
                    # and construct the list to send for modification.
                    sendLines = [0]*len(searchLines[rxnNum])
                    for n in range(len(searchLines[rxnNum])):
                        sendLines[n] = lines[searchLines[rxnNum][n]]

                    # If structure to check which type of auxiliary
                    # information is present and send the proper
                    # compiled regular expression to auxcheck. `ret` is
                    # the returned list of modified lines.
                    if extraInfo[rxnNum] == 1:
                        ret = auxcheck(sendLines, lowmatch, multfactor)
                    elif extraInfo[rxnNum] == 2:
                        ret = auxcheck(sendLines, highmatch, multfactor)
                    elif extraInfo[rxnNum] == 3:
                        ret = auxcheck(sendLines, revmatch, multfactor)
                    elif extraInfo[rxnNum] == 4:
                        ret = auxcheck(sendLines, plogmatch, multfactor)
                    elif extraInfo[rxnNum] == 5:
                        ret = chebcheck(sendLines, multfactor)

                    # Loop through the returned lines and set the
                    # correct line in the `outLines` list to the
                    # modified lines.
                    for n in range(len(searchLines[rxnNum])):
                        outLines[searchLines[rxnNum][n]] = ret[n]

                # Create a folder in which simulations will be run,
                # after checking for its existence.
                chemfolder = 'Reaction' + str(rxnNum + 1)
                if not os.path.exists(chemfolder):
                    os.makedirs(chemfolder)

                # Copy the various files we will need to run the
                # simulation into the simulation directory.
                shutil.copyfile(inpfile, os.path.join(chemfolder, inpfile))
                shutil.copyfile('CKSolnList.txt', os.path.join(chemfolder,
                    'CKSolnList.txt'))
                shutil.copyfile(os.path.join(reactiondir, 'data',
                                'chemkindata.dtd'), os.path.join(chemfolder,
                                'chemkindata.dtd')
                                )

                # If the thermo data is in the chemistry file, we don't
                # have to copy therm.dat
                if not thermInChem:
                    shutil.copyfile(thermfilename, os.path.join(chemfolder,
                        thermfilename))

                # Change directory into the simulation directory.
                with cd(chemfolder):

                    # Set the filename for the modified chemistry input
                    # file. Open the modified chemistry input file with
                    # write access, and write the file. This write is
                    # buffered. Close the modified chemistry input file.
                    chemfilename = 'chem' + str(rxnNum + 1) + '.inp'
                    with open(chemfilename, 'wt') as chemfile:
                        for outLine in outLines:
                            chemfile.write(outLine)

                    # Call the CHEMKIN-Pro interpreter, then the solver,
                    # then the post-processor, then the transpose
                    # utility to create the solution .csv files. First
                    # check if we need the thermo file.
                    if thermInChem:
                        subprocess.call([ckinterp, '-i', chemfilename, '-o',
                                        chemoutput, '-c', chemasc]
                                        )
                    else:
                        subprocess.call([ckinterp, '-i', chemfilename, '-o',
                                        chemoutput, '-d', thermfilename, '-c',
                                        chemasc]
                                        )
                    subprocess.call([reactor, '-i', inpfile, '-o',
                                    simoutputfile, 'Pro', '-c', chemasc]
                                    )
                    subprocess.call(['GetSolution', 'CKSolnList.txt',
                                    'XMLdata.zip']
                                    )
                    subprocess.call(['CKSolnTranspose'])

                    # Open, read, and close the file with the solution
                    # information.
                    with open('CKSoln_solution_point_value_vs_solution_'
                              'number.csv', 'r') as outputFile:
                        ignLines = outputFile.readlines()

                    # Find the columns with 'Ignition' in the title -
                    # these are the ignition delays. Then, convert the
                    # ignition delay to a float.
                    ignCol = [x for x, val in enumerate(ignLines[0].split(','))
                              if 'Ignition' in val
                              ]
                    ignDelay = [float(k) for k in
                                [ignLines[1].split(',')[x].strip() for x in
                                ignCol]
                                ]

                    # Create a list for writing to the output file,
                    # including the corrected (i.e. one-based) reaction
                    # number, the multiplication factor, and the
                    # ignition delay. Format the list into a comma-
                    # separated format and convert to a string. Then
                    # append a newline and print the list to the
                    # sensitivity output file.
                    ignSens = [rxnNum + 1, multfactor, '', '',
                               reacmatch.search(line).group(1).strip()
                               ]
                    ignSens[2:2] = ignDelay
                    printsens = ','.join(map(str, ignSens))
                    tignsens.write(printsens + '\n')
                    tignsens.flush()

                # Remove the simulation directory.
                shutil.rmtree(chemfolder)

                # Print to the screen some progress information.
                caseNo = i + 1 + j*len(wantreactions)
                print('Case {0} of {1} \nReaction #: {2} \nIgnition Delay:'
                      '{3}\nInput File: {4}\nFactor: {5}'.format(caseNo,
                      totalCases, rxnNum + 1, ignDelay, inpfile,
                      multfactor)
                      )

if __name__ == '__main__':
    main()
