import pandas as pd
import sklearn.linear_model
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import KBinsDiscretizer

def preprocess(data):

    # Replace missing values with mode
    imputer = SimpleImputer(missing_values='?', strategy="most_frequent")
    data.iloc[:,:] = imputer.fit_transform(data)
    
    # Replace categories with int values since scikit-learn does not handle strings
    categories = ["workclass", "education", "marital.status", "occupation", 
                  "relationship", "race", "sex", "native.country"]
    le = LabelEncoder()
    for category in categories:
        data[category] = le.fit_transform(data[category])

    # Replace continuous values with split on median
    categories = ["age", "fnlwgt", "education.num", "capital.gain", 
                  "capital.loss", "hours.per.week"]
    est = KBinsDiscretizer(n_bins=2, encode="ordinal", strategy="uniform")
    for category in categories:
        data[category] = est.fit_transform(data[[category]])

    return data

def main():
    train = pd.read_csv("CourseProject/train_final.csv", header = 0)
    train_X = train.iloc[:,:-1]
    train_y = train.iloc[:,-1]

    train_X = preprocess(train_X)
    classifier = RandomForestClassifier(n_estimators = 20, random_state = 0)
    classifier.fit(train_X, train_y)

    test = pd.read_csv("CourseProject/test_final.csv", header = 0)
    test_X = test.iloc[:,1:]

    test_X = preprocess(test_X)
    test_y = classifier.predict(test_X)

    out = pd.DataFrame({'ID' : test.ID, 'Prediction' : test_y})
    out.set_index('ID').to_csv("CourseProject/results.csv")
    pass

main()