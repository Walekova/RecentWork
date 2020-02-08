#!/usr/bin/env python
"""
Mapper reads in text documents and emits word counts by class.
INPUT:                                                    
    DocID \t true_class \t subject \t body                
OUTPUT:                                                   
    partitionKey \t word \t class0_partialCount,class1_partialCount       
    

Instructions:
    You know what this script should do, go for it!
    (As a favor to the graders, please comment your code clearly!)
    
    A few reminders:
    1) To make sure your results match ours please be sure
       to use the same tokenizing that we have provided in
       all the other jobs:
         words = re.findall(r'[a-z]+', text-to-tokenize.lower())
         
    2) Don't forget to handle the various "totals" that you need
       for your conditional probabilities and class priors.
       
Partitioning:
    In order to send the totals to each reducer, we need to implement
    a custom partitioning strategy.
    
    We will generate a list of keys based on the number of reduce tasks 
    that we read in from the environment configuration of our job.
    
    We'll prepend the partition key by hashing the word and selecting the
    appropriate key from our list. This will end up partitioning our data
    as if we'd used the word as the partition key - that's how it worked
    for the single reducer implementation. This is not necessarily "good",
    as our data could be very skewed. However, in practice, for this
    exercise it works well. The next step would be to generate a file of
    partition split points based on the distribution as we've seen in 
    previous exercises.
    
    Now that we have a list of partition keys, we can send the totals to 
    each reducer by prepending each of the keys to each total.
       
"""

import re                                                   
import sys                                                  
import numpy as np      

from operator import itemgetter
import os

#################### YOUR CODE HERE ###################
   
# helper functions
def getPartitions(reduce_tasks):
    """
    Returns:    partition_keys (sorted list of strings)
   
    """    
    # use the first N uppercase letters as custom partition keys
    N = int(reduce_tasks)
    KEYS = list(map(chr, range(ord('A'), ord('Z')+1)))[:N]
    partitions = []
        
    for key in KEYS:
        partitions.append([key, makeKeyHash(key, reduce_tasks)])
    
    parts = sorted(partitions,key=itemgetter(1))
    partition_keys = list(np.array(parts)[:,0])
    partition_file = np.arange(0,N,N/(reduce_tasks))[::-1]
    
    return partition_keys, partition_file

# helper functions
def makeKeyHash(key, num_reducers):
    """
    Mimic the Hadoop string-hash function.
    
    key             the key that will be used for partitioning
    num_reducers    the number of reducers that will be configured
    """
    byteof = lambda char: int(format(ord(char), 'b'), 2)
    current_hash = 0
    for c in key:
        current_hash = (current_hash * 31 + byteof(c))
    return current_hash % num_reducers

# read number of reduce tasks
if os.getenv('mapreduce_job_reduces') == None:
    reduce_tasks = 1
else:
    reduce_tasks = int(os.getenv('mapreduce_job_reduces'))

# initialize variables
partition_keys, partition_file = getPartitions(reduce_tasks)
spamTotal, hamTotal, spamWordTotal, hamWordTotal = 0,0,0,0
UniqueWords = 0

# process the input line by line
for line in sys.stdin:
    # parse input and tokenize
    docID, _class, subject, body = line.lower().split('\t')
    words = re.findall(r'[a-z]+', subject + ' ' + body)
    spamCount, hamCount = 0,0
    
    if int(_class) == 1:
        spamTotal += 1
    else:
        hamTotal += 1  
  
    for word in words:
        if int(_class) == 1:
            spamCount = 1
            spamWordTotal += 1
                
        else:
            hamCount = 1
            hamWordTotal += 1
            
        # Prepend the approriate key by finding the bucket, and using the index to fetch the key.
        for idx in range(len(partition_keys)):
            if makeKeyHash(word[0],reduce_tasks) == partition_file[idx]:       
                print(f"{partition_keys[idx]}\t{word}\t{hamCount}\t {spamCount}")
                #UniqueWords +=1

# Class Priors for model
for idx in range(len(partition_keys)):            
    if makeKeyHash('C',reduce_tasks) == partition_file[idx]:
        print(f"{partition_keys[idx]}\t{'ClassPriors'}\t{hamTotal}\t{spamTotal}")

# Auxiliary subtotals        
for idx in range(len(partition_keys)):            
    print(f"{partition_keys[idx]}\t{'!ClassWords'}\t{hamWordTotal}\t{spamWordTotal}")
    #print(f"{partition_keys[idx]}\t{'!ClassNumber'}\t{UniqueWords}\t{UniqueWords}")
#################### (END) YOUR CODE ###################