def mechinterp(lines):
    """Interpret CHEMKIN chemistry input files and return lists of line
    numbers and reaction info.

    INPUT:
    lines - list of strings, lines of the CHEMKIN format chemistry input file
    numRxns - integer, number of reactions in the input mechanisms
    OUTPUT:
    reaction_lines - list of integers, line numbers of reactions in the input set
                of lines
    search_lines - list of lists of integers, line numbers of the lines between
                  the reactions
    extra_info - list of integers, status of auxiliary information for a
                reaction
                    0 - no auxiliary information
                    1 - LOW parameter specified
                    2 - HIGH parameter specified
                    3 - REV reaction specified
                    4 - PLOG reaction specified
                    5 - CHEB reaction specified
    therm_in_chem - boolean indicating the status of the thermodynamic data.
                  False - thermo data is stored in a separate file
                  True - thermo data is stored in the chemistry file

    """

    # Import the module for regular expressions.
    import re

    # Compile regular expressions for each of the expected keywords to
    # be encountered. (?i) indicates ignore case.
    reactionmatch = re.compile(r'=(?!.*\!)')
    commentmatch = re.compile(r'^\!')
    newlinematch = re.compile(r'^\n')
    lowmatch = re.compile(r'(?i)^[\s]*LOW')
    highmatch = re.compile(r'(?i)^[\s]*HIGH')
    dupmatch = re.compile(r'(?i)\bDUP\b|\bDUPLICATE\b')
    endmatch = re.compile(r'(?i)^END')
    revmatch = re.compile(r'(?i)^[\s]*REV')
    plogmatch = re.compile(r'(?i)^[\s]*PLOG')
    chebmatch = re.compile(r'(?i)^[\s]*CHEB')
    thermmatch = re.compile(r'(?i)THERM ALL|THERMO ALL')

    # Initialize 'reaction_number', a counter of the number of reactions,
    # and 'reaction_lines', a zero-based list of the line numbers of the
    # reactions in the input file. Set the 'numRxns' element of the
    # 'reaction_lines' list to the number of lines in the input file so that
    # it can be used as a search parameter later.
    reaction_number = 0
    reaction_lines = []

    # Begin a loop over all of the lines in the input file. The lines
    # are stored in the variable 'line' for each iteration.
    for line_number, line in enumerate(lines):

        # We have to reverse the line to properly check for a reaction.
        # This eliminates the case where an auxiliary line may contain
        # an = sign in a comment, which would otherwise be included in
        # the reaction list. Since Python does not allow variable length
        # look behind, the workaround is to reverse the string and use
        # variable length look ahead.
        line = line[::-1]

        # Check for lines that are reactions, defined by the
        # reactionmatch regular expression
        rxncond = reactionmatch.search(line)

        # If the reaction condition contains information the line is a
        # reaction. Put the line number of this reaction in the
        # 'reaction_lines' list, and increment the reaction counter. Remember
        # that since Python is zero-based, the real reaction number of a
        # reaction will be one more than the number from this loop
        if rxncond is not None:
            reaction_lines.append(line_number)
            reaction_number += 1

    # Append the last line number to the reaction_lines list so that it can
    # be used to determine the `search_lines` - see below.
    reaction_lines.append(len(lines))

    # Initialize two lists to hold information about the reactions.
    # 'search_lines' is a list of lists of the line numbers between each
    # reaction. 'extra_info' is a list of integers corresponding to each
    # type of reaction rate modification.
    search_lines = []
    extra_info = [0 for i in range(len(reaction_lines)-1)]

    # Begin loop to find and read all of the lines between each reaction
    # to check for auxiliary information.
    for i in range(len(reaction_lines)-1):

        # Fill the ith element of 'search_lines' with a list of lines
        # in the input file between the line number in the ith element
        # of 'reaction_lines' and the line number in the (i+1)th element. Add
        # 1 to the first line number to avoid the reaction line itself.
        # The 'range' function automatically excludes the last number in
        # the range, which would be the next reaction, so there is no
        # need to subtract one from the second line number.
        search_lines.append(list(range(reaction_lines[i]+1, reaction_lines[i+1])))

        # Loop over the line numbers in the previously appended (i.e.
        # last) element of 'search_lines' to look for auxiliary
        # information.
        for line_number in search_lines[-1]:
            line = lines[line_number]

            # Check if the line is a comment or blank.
            blankcond = newlinematch.match(line)
            comcond = commentmatch.match(line)
            if blankcond is None and comcond is None:

                # Use an if/elif block to check whether the current line
                # contains any auxiliary information. The options 'LOW',
                # 'HIGH', 'REV', 'PLOG', and 'CHEB' are mutually
                # exclusive, so there should be no chance of a different
                # type being present. Therefore, break out of the loop
                # through `search_lines[i]` when a keyword is found.
                lowcond = lowmatch.search(line)
                highcond = highmatch.search(line)
                revcond = revmatch.search(line)
                plogcond = plogmatch.search(line)
                chebcond = chebmatch.search(line)
                if lowcond is not None:
                    extra_info[i] = 1
                    break
                elif highcond is not None:
                    extra_info[i] = 2
                    break
                elif revcond is not None:
                    extra_info[i] = 3
                    break
                elif plogcond is not None:
                    extra_info[i] = 4
                    break
                elif chebcond is not None:
                    extra_info[i] = 5
                    break

    # Check if the thermo data is included in the chemistry. Store the
    # result in the `therm_in_chem` boolean, where `True` indicates that
    # no separate thermo file is required.
    for line in lines:
        if thermmatch.search(line) is not None:
            therm_in_chem = True
            break
        else:
            therm_in_chem = False

    # Return the output information
    return reaction_lines, search_lines, extra_info, therm_in_chem,
