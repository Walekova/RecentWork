#!/usr/bin/env python
"""
Reducer aggregates word counts by class and emits frequencies.

INPUT:
    partitionKey \t word \t class0_partialCount,class1_partialCount  
OUTPUT:
    word \t {spamCount, hamCount, ham_cProb, spam_cProb}
    
Instructions:
    Again, you are free to design a solution however you see 
    fit as long as your final model meets our required format
    for the inference job we designed in Question 8. Please
    comment your code clearly and concisely.
    
    A few reminders: 
    1) Don't forget to emit Class Priors (with the right key).
    2) In python2: 3/4 = 0 and 3/float(4) = 0.75
"""
##################### YOUR CODE HERE ####################
import sys

# initiatlize trackers
cur_word = None
cur_count = 0
hamCount, spamCount, hamWordCount, spamWordCount, condHam, condSpam = 0,0,0,0,0,0

for line in sys.stdin:
    p_key, word, ham_cts, spam_cts = line.split()

    # get number of total words in ham / spam
    if word == '!ClassWords':
        hamWordCount += int(ham_cts)
        spamWordCount += int(spam_cts)

    elif cur_word == None:
        cur_count += 1
        # make sure the first record is counted properly
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)     
        cur_word = word
        
    elif word == cur_word:
        cur_count += 1
        # tally counts for repeated words
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)  
    
    else:
        if cur_word == 'ClassPriors':
            condHam = hamCount / (hamCount + spamCount)
            condSpam = spamCount / (hamCount + spamCount)
            
        else:
            condHam = float((hamCount) / (hamWordCount))
            condSpam = float((spamCount) / (spamWordCount))    
            
            # prep for reducer / trained model = log(1) = 0
            if condHam == 0:
                condHam = 1
            if condSpam == 0:
                condSpam = 1   

        print(f"{cur_word}\t{hamCount},{spamCount},{condHam},{condSpam}")   
        
        # clear trackers
        hamCount, spamCount, condHam, condSpam, cur_count = 0,0,0,0,0
        checkHamWords, checkSpamWords = 0,0
        
        cur_count += 1
        hamCount += int(ham_cts)
        spamCount += int(spam_cts)  
        cur_word = word

condHam = float((hamCount) / (hamWordCount))
condSpam = float((spamCount) / (spamWordCount))  

# prep for reducer / trained model = log(1) = 0
if condHam == 0:
    condHam = 1
if condSpam == 0:
    condSpam = 1  

    
#print last record
print(f"{cur_word}\t{hamCount},{spamCount},{condHam},{condSpam}")   
##################### (END) CODE HERE ####################