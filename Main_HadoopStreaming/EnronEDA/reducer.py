#!/usr/bin/env python
"""
Reducer takes words with their class and partial counts and computes totals.
INPUT:
    word \t class \t partialCount 
OUTPUT:
    word \t class \t totalCount  
"""
import re
import sys

# initialize trackers
current_word = None
spam_count, ham_count = 0,0

# read from standard input
for line in sys.stdin:
    # parse input
    word, is_spam, count = line.split('\t')
    
############ YOUR CODE HERE #########
    # start counting from first word
    if current_word == None:
        current_word = word
        
    # tally counts from current key
    if word == current_word: 
        if is_spam == '1':
            spam_count += int(count)
        else:
            ham_count += int(count)
    else:
        print(f'{current_word}\t{1}\t{spam_count}')
        print(f'{current_word}\t{0}\t{ham_count}')
        current_word, spam_count, ham_count = word, 0, 0
        if is_spam == '1':
            spam_count += int(count)
        else:
            ham_count += int(count)
            
# don't forget the last record! 
print(f'{current_word}\t{1}\t{spam_count}')
print(f'{current_word}\t{0}\t{ham_count}')
############ (END) YOUR CODE #########