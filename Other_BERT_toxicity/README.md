# DeepLearning - HW04

## Answer questions

#### Name all the layers in parameters in the network, make sure you understand what they do. 
1. Input layer (24x24x1)
2. Convolution layer - 8 5x5 filters padded by 2 - relu activation 
3. Pool layer - perform max pooling in 2x2 non-overlapping neighborhoods
4. Convolution layer - 16 5x5 filters padded by 2 - relu activation 
5. Pool Layer - perform max pooling in 3x3 non-overlapping neighborhoods
6. Deep layer softmax with 10 classifications
 
#### Experiment with the number and size of filters in each layer. Does it improve the accuracy?
larger size and greater number of filters seem to slow down the convergence with no noticeable improvement in accuracy (keeping to exmaples seen up to 5000)

#### Remove the pooling layers. Does it impact the accuracy?
It is slower and it overfits.

#### Add one more conv layer. Does it help with accuracy?
It is faster.

#### Increase the batch size. What impact does it have?
I am finding it hard to spot the difference however it seems to have brought in some noise.

#### What is the best accuracy you can achieve? Are you over 99%? 99.5%? 
95%

## Work with Jupyter notebook

see in repository
