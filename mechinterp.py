def mechinterp(lines, numRxns):
    """Interpret CHEMKIN chemistry input files and return lists of line numbers and reaction info.

    INPUT:
    lines - list of strings, lines of the CHEMKIN format chemistry input file
    numRxns - integer, number of reactions in the input mechanims
    OUTPUT:
    reacLines - list of integers, line numbers of reactions in the input set of lines
    searchLines - list of lists of integers, line numbers of the lines between the reactions
    extraInfo - list of integers, status of auxiliary information for a reaction
                0 - no auxiliary information
                1 - LOW parameter specified
                2 - HIGH parameter specified
                3 - REV reaction specified
                4 - PLOG reaction specified
                5 - CHEB reaction specified
    
    """
#
#Begin function
#
    #
    #Import the module for regular expressions
    #
    import re
    #
    #Compile regular expressions for each of the expected keywords to be
    #encountered. (?i) indicates ignore case.
    #
    reactionmatch = re.compile(r'=(?!.*\!)') #Match any equals signs not followed by an exclamation point
    commentmatch = re.compile(r'^\!') # Match exclamation points at the beginning of the string
    newlinematch = re.compile(r'^\n') # Match newlines if they're the first character in the string
    lowmatch = re.compile(r'(?i)^[\s]*LOW')
    highmatch = re.compile(r'(?i)^[\s]*HIGH')
    dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
    endmatch = re.compile(r'(?i)^END')
    revmatch = re.compile(r'(?i)^[\s]*REV')
    plogmatch = re.compile(r'(?i)^[\s]*PLOG')
    chebmatch = re.compile(r'(?i)^[\s]*CHEB')
    #
    #Initialize 'reactionNum', a counter of the number of reactions, and
    #'reacLines', a zero-based list of the line numbers of the reactions
    #in the input file. Set the 'numRxns' element of the 'reacLines' 
    #list to the number of lines in the input file so that it can be 
    #used as a search parameter later.
    #
    reactionNum = 0
    reacLines = [0]*numRxns
    reacLines.insert(numRxns,len(lines))
    #
    #Begin a loop over all of the lines in the input file. The lines are
    #stored in the variable 'line' for each iteration.
    #
    for lineNum in range(len(lines)):
        #
        #We have to reverse the line to properly check for a reaction.
        #This eliminates the case where an auxiliary line may contain
        #an = sign in a comment, which would otherwise be included in
        #the reaction list. Since Python does not allow variable length
        #look behind, the workaround is to reverse the string and use
        #variable length look ahead.
        #
        line = lines[lineNum][::-1]
        #
        #Check for lines that are reactions, defined by the
        #reactionmatch regular expression
        rxncond = reactionmatch.search(line)
        #
        #If the reaction condition contains information the line is a 
        #reaction. Put the line number of this reaction in the 
        #'reacLines' list, and increment the reaction counter. Remember 
        #that since Python is zero-based, the reaction number of a
        # reaction will be one more than the number from this loop
        #
        if rxncond is not None:
            reacLines[reactionNum] = lineNum
            reactionNum += 1
        #
        #End if
        #
    #
    #End loop
    #
    #
    #Initialize two lists to hold information about the reactions.
    #'searchLines' is a list of lists of the line numbers between each
    #reaction. 'extraInfo' is a list of integers corresponding to each
    #type of reaction rate modification.
    #
    searchLines = [0]*numRxns
    extraInfo = [0]*numRxns
    #
    #Begin loop to find and read all of the lines between each reaction
    #to check for auxiliary information.
    #
    for i in range(len(reacLines)-1):
        #
        #Fill the ith element of 'searchLines' with a list of lines
        #in the input file between the line number in the ith element
        #of 'reacLines' and the line number in the (i+1)th element. Add
        #1 to the first line number to avoid the reaction line itself.
        #The 'range' function automatically excludes the last number in
        #the range.
        #
        searchLines[i] = list(range(reacLines[i]+1,reacLines[i+1]))
        #
        #Loop over the line numbers in the ith element of 'searchLines'
        #to look for auxiliary information.
        #
        for lineNum in searchLines[i]:
            line = lines[lineNum]
            #
            #Check if the line is a comment or blank
            #
            blankcond = newlinematch.match(line)
            comcond = commentmatch.match(line)
            if blankcond is None and comcond is None:
                #
                #Use an if/elif block to check whether the current line
                #contains any auxiliary information. The options 'LOW',
                #'HIGH', 'REV', 'PLOG', and 'CHEB' are mutually
                #exclusive, so there should be no chance of a different
                #type overwriting a previous type.
                #
                lowcond = lowmatch.search(line)
                highcond = highmatch.search(line)
                revcond = revmatch.search(line)
                plogcond = plogmatch.search(line)
                chebcond = chebmatch.search(line)
                if lowcond is not None:
                    extraInfo[i:i+1] = [1]
                elif highcond is not None:
                    extraInfo[i:i+1] = [2]
                elif revcond is not None:
                    extraInfo[i:i+1] = [3]
                elif plogcond is not None:
                    extraInfo[i:i+1] = [4]
                elif chebcond is not None:
                    extraInfo[i:i+1] = [5]
                #
                #End if/elif
                #
            #
            #End if
            #
        #
        #End loop
        #
    #
    #End Loop
    #
    return (reacLines, searchLines, extraInfo)
#
#End function
#
