import pandas as pd
import sklearn.linear_model
#from sklearn.neural_network import MLPClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.ensemble import RandomForestClassifier

class RandomForest():

    def __init__(self, estimators=20, imputer="most_frequent", n_bins = 2, 
                 encode="ordinal", discrete="uniform"):
        #self.classifier = MLPClassifier()
        self.classifier = RandomForestClassifier(n_estimators=estimators)
        self.imputer = imputer
        self.n_bins = n_bins
        self.encode = encode
        self.discrete = discrete
        pass

    def preprocess(self, data):
        str_categories = ["workclass", "education", "marital.status", "occupation", 
                  "relationship", "race", "sex", "native.country"]
        num_categories = ["age", "fnlwgt", "education.num", "capital.gain", 
                    "capital.loss", "hours.per.week"]
        
        # Replace missing values with mode
        imputer = SimpleImputer(missing_values='?', strategy=self.imputer)
        data.iloc[:,:] = imputer.fit_transform(data)
    
        # Replace categories with int values since scikit-learn does not handle strings
        le = LabelEncoder()
        for category in str_categories:
            data[category] = le.fit_transform(data[category])

        # Replace continuous values with split on median
        est = KBinsDiscretizer(n_bins=self.n_bins, 
                               encode=self.encode, strategy=self.discrete)
        for category in num_categories:
            data[category] = est.fit_transform(data[[category]])
        return data

    def fit(self, train_X, train_y):
        train_X = self.preprocess(train_X)
        self.classifier.fit(train_X, train_y)
        pass

    def predict(self, test_X):
        test_X = self.preprocess(test_X)
        return self.classifier.predict(test_X)

    def accuracy(self, test_X, test_y):
        acc = 0
        test_X = self.preprocess(test_X)
        out = self.classifier.predict(test_X)
        for i in range(len(test_y)):
            if test_y[i] == out[i]:
                acc += 1
            pass
        return acc/len(test_y)

    pass

def sample_test():
    data = pd.read_csv("CourseProject/train_final.csv", header = 0)
    train = data.sample(frac=1/10)
    toprint = []
    for i in range(2, 3):
        train_X = train.iloc[:,:-1]
        train_y = train.iloc[:,-1]
        test_X = data.iloc[:,:-1]
        test_y = data.iloc[:,-1]
        classifier = RandomForest(estimators=50, n_bins=10, discrete="uniform")
        classifier.fit(train_X, train_y)
        toprint.append(str(i) + ", " + str(classifier.accuracy(test_X, test_y)))
        pass
    for p in toprint:
        print(p)
    pass

def main():

    train = pd.read_csv("CourseProject/train_final.csv", header = 0)
    train_X = train.iloc[:,:-1]
    train_y = train.iloc[:,-1]

    classifier = RandomForest(estimators=200 , n_bins=100, discrete="uniform")
    classifier.fit(train_X, train_y)

    test = pd.read_csv("CourseProject/test_final.csv", header = 0)
    test_X = test.iloc[:,1:]
    test_y = classifier.predict(test_X)

    out = pd.DataFrame({'ID' : test.ID, 'Prediction' : test_y})
    out.set_index('ID').to_csv("CourseProject/results.csv")
    pass

main()