# 50.007 Machine Learning Sentiment Analysis Project

A sentiment analysis project of various tweets in English, Spanish and Chinese using Hidden Markov Models.
Visit https://github.com/iyool/ml-project to view this README in properly-styled MarkDown.


### Part 2 : Getting optimal Y sequence by maximum probability of y

On Windows:
````
$ python ml_hmm_p2.py {path to input data file} {path to training data file} W
````
On MacOS/Linux:
````
$ python3 ml_hmm_p2.py {path to input data file} {path to training data file} L
````
Example:
````
$ python3 ml_hmm_p2.py EN/dev.in EN/train L
````


### Part 3 : Getting optimal Y sequence using the Viterbi algorithm

On Windows:
````
$ python ml_hmm_p3.py {path to input data file} {path to training data file} W
````
On MacOS/Linux:
````
$ python3 ml_hmm_p3.py {path to input data file} {path to training data file} L
````
Example:
````
$ python3 ml_hmm_p3.py EN/dev.in EN/train L
````


### Part 4 : Getting k-th best Y sequence in Viterbi

On Windows:
````
$ python ml_hmm_p4.py {k value} {path to input data file} {path to training data file} W
````
On MacOS/Linux:
````
$ python3 ml_hmm_p4.py {k_value} {path to input data file} {path to training data file} L
````
Example:
````
$ python3 ml_hmm_p4.py 5 EN/dev.in EN/train L
````


### Part 5 : Improvement on HMM

On Windows:
````
$ python ml_hmm_p5.py {path to input data file} {path to training data file} {name of output file} W
````
On MacOS/Linux:
````
$ python3 ml_hmm_p5.py {path to input data file} {path to training data file} {name of output file} L
````
Example:
````
$ python3 ml_hmm_p5.py test/EN/test.in EN/train test.p5.out L
````

Do note that the output file will be written in the same directory as the input data.
