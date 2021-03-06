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
