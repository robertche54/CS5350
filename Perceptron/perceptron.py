import math
import random
import sys

data = []

def read(filename):
    with open (filename, 'r') as f:
        for line in f:
            terms = line.split(',')
            row = []
            for term in terms:
                row.append(float(term))
                pass
            data.append(row)
            pass
        pass
    post_process()
    pass

def post_process():
    for i in range(len(data)):
        data[i][-1] = 2*data[i][-1] - 1
    pass

def standard_perceptron(epochs, r, weights = None, shuffle = False):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * y
    while epochs != 0:
        # optional to shuffle the data between each epoch
        if shuffle:
            random.shuffle(data)
        for i in range(len(data)):
            # prediction = weights[y]
            prediction = 0
            for j in range(y):
                prediction += data[i][j] * weights[j]
            if prediction * data[i][y] <= 0:
                for j in range(y):
                    weights[j] += r * data[i][y] * data[i][j]
            pass
        epochs -= 1
        pass
    return weights

def voted_perceptron(epochs, r, weights = None):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * y
    votes = []
    count = 0
    while epochs != 0:
        for i in range(len(data)):
            # prediction = weights[y]
            prediction = 0
            for j in range(y):
                prediction += data[i][j] * weights[j]
            if prediction * data[i][y] <= 0:
                votes.append((count, weights.copy()))
                for j in range(y):
                    weights[j] += r * data[i][y] * data[i][j]
                count = 1
            else:
                count += 1
            pass
        epochs -= 1
        pass
    return votes

def averaged_perceptron(epochs, r, weights = None):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * y
    average = [0] *  y
    while epochs != 0:
        for i in range(len(data)):
            # prediction = weights[y]
            prediction = 0
            for j in range(y):
                prediction += data[i][j] * weights[j]
            if prediction * data[i][y] <= 0:
                for j in range(y):
                    weights[j] += r * data[i][y] * data[i][j]
            for j in range(y):
                average[j] += weights[j]
            pass
        epochs -= 1
        pass
    return average

def voted_test(votes):
    acc = 0
    for line in data:
        prediction = 0
        for m in range(len(votes)):
            weight = 0
            for i in range(len(votes[0][1])):
                weight += line[i]*votes[m][1][i]
            prediction += votes[m][0] * math.copysign(1, weight)
            pass
        if prediction * line[-1] >= 0:
            acc += 1
        pass
    return acc/len(data)

def test(weights):
    acc = 0
    for line in data:
        prediction = 0
        for i in range(len(weights)):
            prediction += weights[i] * line[i]
        if prediction * line[-1] >= 0:
            acc += 1
        pass
    return acc/len(data)

def main(argv):
    read(argv[1])
    weights = []
    if argv[3] == "standard_perceptron":
        weights = standard_perceptron(argv[4], argv[5])
        read(argv[2])
        print(weights)
        print(test(weights))
    elif argv[3] == "averaged_perceptron":
        weights = averaged_perceptron(argv[4], argv[5])
        read(argv[2])
        print(weights)
        print(test(weights))
    elif argv[3] == "voted_perceptron":
        weights = voted_perceptron(argv[4], argv[5])
        for line in weights:
            print(line)
        read(argv[2])
        print(voted_test(weights))
    pass

if __name__ == "__main__":
    # argv = ["perceptron.py", "Perceptron/train.csv", "Perceptron/test.csv", "standard_perceptron", 10, 0.01]
    main(sys.argv)
