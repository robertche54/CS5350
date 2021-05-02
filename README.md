# CS5350
This is a machine learning library developed by Robert Che for CS5350 in University of Utah.

## Decision Tree
training_data.csv and testing_data.csv should be in the same directory as decisiontree.py <br />
The first rows for both should be dedicated to column attributes/labels.
```
decisiontree.py training_data.csv testing_data.csv gain_type replace_unknown max_size
```
- gain_type = entropy, majority_error or gini_index
- replace_unknown = yes or no
- max_size = initial max depth of the tree, will build trees and test them from max_size to 0 (6 is a good number to set it to)
###### Example
`decisiontree.py bank.csv bank-full.csv entropy yes 1`

## Ensemble Learning
training_data.csv and testing_data.csv should be in the same directory as the .py files <br />
The first rows for both should be dedicated to column attributes/labels.
```
adaboost.py training_data.csv testing_data.csv iterations
bagging.py training_data.csv testing_data.csv iterations bootstrap_size
randomforest.py training_data.csv testing_data.csv subset_size iterations bootstrap_size
```
- iterations = number of trees/stumps to be built
- bootstrap_size (optional) = number of samples to bootstrap, will be size of the training data by default
- subset_size = size of subset
###### Example
`randomforest.py train.csv test.csv 4 500 5000`

## Linear Regression
training_data.csv and testing_data.csv should be in the same directory as linearregression.py <br />
```
linearregression.py training_data.csv testing_data.csv mode iterations ratio
```
- mode = gradient_descent, stochastic_descent, math
- iterations (optional) = prematurely stops training if iteration count is reached, will be -1 by default (never stops)
- ratio (optional) = multiplies the weights, will use the pre-selected ones by default
###### Example
`linearregression.py train.csv test.csv gradient_descent -1 0.0078125`

## Perceptron

training_data.csv and testing_data.csv should be in the same directory as perceptron.py <br />
```
perceptron.py training_data.csv testing_data.csv mode epochs ratio
```
- mode = standard_perceptron, voted_perceptron, average_perceptron
- epochs = number of cycles through data
- ratio = multiplies the weights
###### Example
`perceptron.py train.csv test.csv standard_perceptron 10 0.01`

## SVM

training_data.csv and testing_data.csv should be in the same directory as svm.py <br />
```
svm.py training_data.csv testing_data.csv primal_svm C epochs gamma d
svm.py training_data.csv testing_data.csv dual_svm C 
```
- epochs = number of cycles through data
- gamma = part of learning rate
- d = part of learning rate, set to 0 for optional
###### Example
`svm.py train.csv test.csv primal_svm 100/873 100 0.000001`

