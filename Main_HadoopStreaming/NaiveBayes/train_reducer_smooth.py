#!/usr/bin/env python
"""
Reducer aggregates word counts by class and emits frequencies.

INPUT:
    partitionKey \t word \t class0_partialCount,class1_partialCount  
OUTPUT:
    word \t {spamCount, hamCount, hamCountSmooth, spamCountSmooth}

"""
import sys                                                  
import numpy as np  

#################### YOUR CODE HERE ###################

import sys

# initiatlize trackers
cur_word = None
cur_count = 0
hamCount, spamCount, hamWordCount, spamWordCount, condHam, condSpam = 0,0,0,0,0,0
hamChina, spamChina = 0,0
UniqueWords = 0

for line in sys.stdin:
    p_key, word, ham_cts, spam_cts = line.split()

    # get number of total words in ham / spam
    if word == '!ClassWords':
        hamWordCount = int(ham_cts)
        spamWordCount = int(spam_cts)
    
    # count first record appropriately
    elif cur_word == None:
        cur_count += 1
        # tally word class counts
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)     
        cur_word = word
    
    # tally repeated word
    elif word == cur_word:
        cur_count += 1
        # tally word class counts
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)  
    
    else:
        
        if cur_word == 'ClassPriors':
            # prepare Class Priors
            condHam = (hamCount) / (hamCount + spamCount)
            condSpam = (spamCount) / (hamCount + spamCount)
            UniqueWords -= 1
        else:
            # add to count
            condHam = (hamCount+1) 
            condSpam = (spamCount+1)  
        
        # print output           
        print(f"{cur_word}\t{hamCount},{spamCount},{condHam},{condSpam}")   
        UniqueWords += 1
        
        # clear trackers
        hamCount, spamCount, condHam, condSpam, cur_count = 0,0,0,0,0
        checkHamWords, checkSpamWords = 0,0
        
        cur_count += 1
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)  
        cur_word = word

condHam = (hamCount+1) 
condSpam = (spamCount+1)  
# last record print
print(f"{cur_word}\t{hamCount},{spamCount},{condHam},{condSpam}")
UniqueWords += 1
# print auxiliary data
print(f"{'!UniqueWords'}\t{UniqueWords},{0},{0},{0}")   
print(f"{'!ClassWords'}\t{hamWordCount},{spamWordCount},{0},{0}")   
#################### (END) YOUR CODE ###################