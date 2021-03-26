import random

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
    pass

def standard_perceptron(epochs, r, shuffle = False, weights = None):
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

def test(weights):
    acc = 0
    for line in data:
        prediction = 0
        for i in range(len(weights)):
            prediction += weights[i] * line[i]
        if prediction * line[len(line)-1] >= 0:
            acc += 1
        pass
    return acc/len(data)

def main():
    read("Perceptron/train.csv")
    weights = standard_perceptron(10, 0.01)
    print(weights)
    read("Perceptron/test.csv")
    print(test(weights))
    pass


main()