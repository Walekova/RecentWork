# Distributed Training & Neural Machine Translation Lab

Nvidia OpenSeq2Seq is a framework for sequence to sequence tasks such as Automatic Speech Recognition (ASR) and Natural Language Processing (NLP), written in Python and TensorFlow. Many of these tasks take a very long to train, hence the need to train on more than one machine. In this week's lab, we'll be training a Transformer-based Machine Translation network on a small English to German WMT corpus.

Training a Transformer-based Machine Translation network on a small English to German WMT corpus.

After 50000 steps, which took approximately 22-23 hrs the model is still not fully trained. The BLUE score, Eval Loss and Learning rate have not levelled out yet. 

#### BLUE Score

![v100a network](Bleu_score.JPG)

#### Eval Loss

![v100a network](eval_loss.JPG)

At about step 48k it looks like the eval_loss started to increase. this could be an indication of overfitting.

#### Network

The transmission is at 0.22 GB/s this means there is still spare capacity given the set up of 1GB network.
The Peak->Recv is at 14 GB/s for V100a. At first sight network does not look like a limiting factor. This seems to be supported by the fact that the peak Peak->Recv for v100b is app 0.24GB/s.

![v100a network](V100a_network.JPG)

v100b

![v100b network](V100b_network.JPG)
