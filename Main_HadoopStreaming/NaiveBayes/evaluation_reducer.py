#!/usr/bin/env python
"""
Reducer to calculate precision and recall as part
of the inference phase of Naive Bayes.
INPUT:
    ID \t true_class \t P(ham|doc) \t P(spam|doc) \t predicted_class
OUTPUT:
    precision \t ##
    recall \t ##
    accuracy \t ##
    F-score \t ##
         
Instructions:
    Complete the missing code to compute these^ four
    evaluation measures for our classification task.
    
    Note: if you have no True Positives you will not 
    be able to compute the F1 score (and maybe not 
    precision/recall). Your code should handle this 
    case appropriately feel free to interpret the 
    "output format" above as a rough suggestion. It
    may be helpful to also print the counts for true
    positives, false positives, etc.
"""
import sys

# initialize counters
FP = 0.0 # false positives
FN = 0.0 # false negatives
TP = 0.0 # true positives
TN = 0.0 # true negatives

# read from STDIN
for line in sys.stdin:
    # parse input
    docID, class_, pHam, pSpam, pred = line.split()
    # emit classification results first
    print(line[:-2], class_ == pred)

    if (int(class_)==0) and (int(pred)==0):
        TN += 1
    elif (int(class_)==0) and (int(pred)==1):
        FP += 1 
    elif (int(class_)==1) and (int(pred)==0):
        FN += 1
    elif (int(class_)==1) and (int(pred)==1):
        TP += 1

# then compute evaluation stats
Total = (TN + TP + FN + FP)
Accuracy = (TN + TP)/(TN + TP + FN + FP)
Precision = TP / (TP +FP)
Recall = TP / (TP + FN)
if (Precision + Recall) == 0:
    FScore = None
else:
    FScore = 2 * (Precision * Recall) / (Precision + Recall)

# print stats
print(f"{'# Documents: '}\t{Total}")    
print(f"{'True Positives:'}\t{TP}")   
print(f"{'True Negatives:'}\t{TN}")
print(f"{'False Positives:'}\t{FP}")
print(f"{'False Negatives:'}\t{FN}")
print(f"{'Accuracy:'}\t{Accuracy}")
print(f"{'Precision:'}\t{Precision}")
print(f"{'Recall:'}\t{Recall}")
print(f"{'F-Score:'}\t{FScore}")

#################### YOUR CODE HERE ###################























#################### (END) YOUR CODE ###################
    