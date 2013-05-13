import re
##from mechinterp import mechinterp
##
##chem = open('mch_chx_v9f2_mech.inp','r')
##lines = chem.readlines()
##chem.close()
##
##numRxns = 6499
##rxnLines = mechinterp(lines,numRxns)[0]
def specRxnNum(rxnLines,lines,numRxns):
    specNum = []
    startSpec = ['mch','mchr1','mchr2','mchr3','mchr4','cychexch2', 'mch1oo','mch2oo','mch3oo',
                 'mch4oo','mch1oj','mch2oj','mch3oj','mch4oj','chxch2oo','chxch2oj','chxdch2',
                 'mch1qj3','mch1ooh','mch1ene','mch1qx','mch3oj','mch1oj','mch1qj4','mch1qj2',
                 'mch2qx','mch2ooh','mch2ene','mch2qj6','mch2qj4','mch2qj5','mch2qj3','mch2qj1',
                 'mch3qj1','mch3ooh','mch3ene','mch3qj5','mch3oj','mch3qj2','mch3qj6','mch4qj2',
                 'mch4ooh','mch4qj1','mch4qj3','mch4oj','chxj2ch2q','chxch2ooh','chxj1ch2q',
                 'chxch2oj','c7ene-one','mchyo24','mchyo25','mchyo23','mch2qxqj','chxyco-2','mcho',
                 'mch2q3qj','mch2q1qj','mch2q4qj','mch2q5qj','mch2q6qj','mch3q2qj','mch3q5qj',
                 'mch3q6qj','mch3q1qj','mch4q3qj','mch4q2qj','mch4q1qj','mchxq1qj','mchxq2qj',
                 'c7enej-one','c7ene-onej']
    for j in range(len(startSpec)):
##        print(startSpec[j])
        specmatch = re.compile(r'\b'+startSpec[j][::-1]+r'\b(?!.*\!)')
        for i in range(numRxns):
            line = lines[rxnLines[i]][::-1]
            if specmatch.search(line) is not None:
                specNum.append(i+1)
    ##        print(line[::-1],end='')

##    print(len(specNum))
    specNum = list(set(specNum))
    print(len(specNum))
    return specNum
