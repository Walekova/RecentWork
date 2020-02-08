#!/usr/bin/env python
"""
Post process to calculate number of unique words and the conditional probabilities for Smoothed model
INPUT:
    word \t {spamCount, hamCount, ham_cProb, spam_cProb}
OUTPUT:
    word \t {spamCount, hamCount, ham_cProb, spam_cProb}

"""
import sys                                                  
import numpy as np  

#################### YOUR CODE HERE ###################

import sys

# Initialize variables
hamWordCount = 0
spamWordCount = 0
unique = 0

# Process input
for line in sys.stdin:
    word, payload = line.split()
    hamCount, spamCount, preCondHam, preCondSpam = payload.split(',')
    
    # Process records
    if word == '!UniqueWords':
        unique += int(hamCount)
    elif word == '!ClassWords':
        hamWordCount += int(hamCount)
        spamWordCount += int(spamCount) 
    elif word == 'ClassPriors':
        print(f"{word}\t{hamCount},{spamCount},{preCondHam},{preCondSpam}")
    else:
        # Calculate conditional probabilities by leveraging the Unique words 
        condHam = float(preCondHam) / (unique + hamWordCount)
        condSpam = float(preCondSpam) / (unique + spamWordCount)
        
        print(f"{word}\t{hamCount},{spamCount},{condHam},{condSpam}")   

#################### (END) YOUR CODE ###################