Python wrapper for sensitivity analysis in CHEMKIN-Pro
==============

This program runs a brute force, one-at-a-time sensitivity analysis of the ignition delay for 
a given mechanism. 

Usage
=====

Download the repository by using git
    
    git clone git://github.com/bryanwweber/pysens.git
    
No other compilation is necessary. Python 3 is required. On Linux, this can be installed
by either

    apt-get install python3
    yum install python3
    ...

depending on your distro. On Windows, Python 3 can be downloaded from the website:
<http://www.python.org/download/>. 

The runtime behavior of the script is configured by setting options in the `pysens.conf` file. A sample 
`pysens.conf` is included in the distribution. 

The script can be run on Linux either by setting the executable bit and executing the program 
from the shell (e.g. `./run_sens.py`), or by calling `python3 run_sens.py`. On Windows, it 
should be run by `py run_sens.py` (Note: I haven't tested this on Windows).

`pysens.conf` options:
======================

The `pysens.conf` file must either have `[DEFAULT]` on the first line, or one of the following
options. No other text is supported on the first line. If options are given that aren't specified
below, they will be ignored.

The options can be specified by:
    
    option = value or option : value

The following options are available:

    reactions - The set of reactions to be analyzed. Can be one of:
                all - use all of the reactions in the mechanism
                comma-separated list (e.g. 1,2,3) - use the specified reactions
                colon-separated values - specify a range of reactions with either
                                         start:stop or start:interval:stop syntax.
                                         If stop is not given, it defaults to the
                                         number of reactions in the mechanism.
                                         Thus, all and 1: are equivalent. end is a
                                         synonym for the number of reactions.
                                         E.g. 1:10 or 1:2:10 or 1:2: or 1:2:end
                                         
    mech input file - The mechanism to be analyzed.
    
    thermo input file - Optional if the thermo information is specified in the
                        mech input file.
    
    outputfile - The base name of the output file. The full output file name will
                 be set by concatentating outputfile + rfactor + sim input file.
                 
    factors - The multiplication factors to be considered. Multiple multiplication
              factors should be separated by commas.
              
    sim input files - Valid CHEMKIN-Pro input files for the test cases desired.
    
    chemkin root - The root directory of the CHEMKIN-Pro install. Accepts shell
                   variables, including those set by the CHEMKIN setup script
                   that should run at logon.