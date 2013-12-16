import re,os
from decimal import *
import configparser
from io import StringIO

class NoSectionConfigParser(configparser.ConfigParser):
    def read(self,filename):
        try:
            text = open(filename).read()
        except IOError:
            pass
        else:
            if not text.startswith('[DEFAULT]'):
                file = StringIO("[DEFAULT]\n" + text)
            else:
                file = StringIO(text)
                
            self.readfp(file,filename)
###############################################################################
def chebcheck(lines,rfac):
    """Take Chebychev auxiliary lines and return lines with modified a_(1,1)

    INPUT:
    lines - list of auxiliary information lines to check
    rfac - rate coefficient  multiplication factor
    OUTPUT:
    lines - list of modified auxiliary information lines

    """
#
#Begin function
#
    #
    #Compile the regular expression to match the Chebychev `a` 
    #coefficients and CHEB keyword.
    #
    Amatch = re.compile(r'(([-+]?[0-9]+(\.[0-9]+)?[eE][-+]?[0-9]+)|([0-9]+(\.[0-9]+)?))')
    chebmatch = re.compile(r'(?i)^[\s]*CHEB')
    #
    #Set a logical for whether or not we've found the first line with a
    #CHEB keyword (not TCHEB or PCHEB).
    #
    firstChebLine = True
    #
    #Convert the input rfactor to log10 of the rfactor. We have to go
    #through the string to arbitrary precision conversion so that we
    #can use arbitrary precision throughout. The conversion to string
    #is not necessary in Python 2.7+ and can be removed in that case.
    #
    rfac = Decimal(rfac)
    addfac = Decimal.log10(rfac)
    #
    #Loop through the input lines
    #
    for lineNum in range(len(lines)):
        line = lines[lineNum]
        chebcond = chebmatch.search(line)
        #
        #If this is a 'CHEB' line and its the first time we've
        #encountered a 'CHEB' line, set `firstChebLine` to `False`
        #
        if chebcond is not None and firstChebLine:
            firstChebLine = False
        #
        #If this is a 'CHEB' line and it is not the first time we've
        #encountered a 'CHEB' line, match the a_(1,1) coefficient, and
        #add log10(rfactor) to it.
        #
        elif chebcond is not None and not firstChebLine:
            acoeff = Amatch.search(line)
            x = Decimal(acoeff.group(1))
            x = x + addfac
            #
            #Format the new a_(1,1) into scientific notation. Replace
            #the correct line in `lines`. Break out of the loop to avoid
            #changing any more coefficients.
            #
            modline = line[:acoeff.start()] + '{0:13.6E}'.format(x)\
                      + line[acoeff.end():]
            lines[lineNum] = modline
            break
    #
    #Return the list of modified lines
    #
    return lines
###############################################################################
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
    #Compile the regular expression to match the Arrhenius coefficients. This
    #is supposed to be different from the Amatch in run_sens.py
    #
    Amatch = re.compile(r'(([-+]?[0-9]+(\.[0-9]+)?[eE][-+]?[0-9]+)|(?<![\d\.])([0]+\.?[0]+)(?![\d]))')
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
            x = Decimal(rfac) * x
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
