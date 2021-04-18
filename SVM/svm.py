import math
import copy
import random

from scipy.optimize import minimize, Bounds, NonlinearConstraint

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

def test(weights, b = 0):
    acc = 0
    for line in data:
        prediction = b
        for i in range(len(weights)):
            prediction += weights[i] * line[i]
        if prediction * line[-1] >= 0:
            acc += 1
        pass
    return acc/len(data)

def distance(a, b):
    d = 0
    for i in range(len(a)):
        d += pow((a[i] - b[i]), 2)
    return math.sqrt(d)
    pass

def primal_svm(epochs, C, gamma, d = 0, weights = None):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * y
    w = copy.copy(weights)
    count = 0
    while count != epochs:
        r = gamma * (1 + count) if d == 0 else gamma/(1 + (gamma/d) * count)
        # prev = copy.copy(w)
        for i in range(len(data)):
            prediction = 0
            for j in range(y):
                prediction += data[i][j] * w[j]
            if prediction * data[i][y] <= 1:
                for j in range(y):
                    # w = w + gCNyx - gw0
                    w[j] += r * C * len(data) * data[i][y] * data[i][j] - r*weights[j]
            else:
                for j in range(y):
                    # w = (1-g)w0
                    weights[j] *= (1 - r)
            pass
        random.shuffle(data)
        count += 1
        # print(distance(prev, w))
        pass
    return w
    pass

def dual_svm_min(x, args):
    sum = 0
    for i in range(len(data)):
        for j in range(len(data)):
            sum += args[i][j] * x[i] * x[j] 
            pass
        sum -= x[i]
        pass
    return 0.5 * sum

def guassian_kernel(i, j, gamma):
    value = 0
    for n in range(len(data[0])-1):
        value += (i[n] - j[n])^2
    return math.exp(-value/gamma)

def data_product(i, j):
    value = 0
    for n in range(len(data[0])-1):
        value += i[n] * j[n]
    return value

def constraint(x):
    sum = 0
    for i in range(len(x)):
        sum += x[i] * data[i][len(data[0])-1]
    return sum

def dual_svm(C, gamma = 0):
    y = len(data[0])-1
    if gamma == 0:
        lookup = [[data_product(data[i], data[j]) * data[i][y] * data[j][y] 
                   for j in range(len(data))] for i in range(len(data))]
    else:
        lookup = [[guassian_kernel(data[i], data[j], gamma) * data[i][y] * data[j][y] 
                   for j in range(len(data))] for i in range(len(data))]
    alpha = [0] * len(data)
    bounds = Bounds([0] * len(data), [C] * len(data))
    constraints = NonlinearConstraint(constraint, 0, 0)
    results = minimize(dual_svm_min, alpha, lookup, method = "SLSQP", 
                       bounds=bounds, constraints=constraints, options = {'disp' : True})
    weights = [0] * y
    for i in range(len(data)):
        for n in range(y):
            # w = sum_i (ai * yi * xi)
            weights[n] += results[i] * data[i][y] * data[i][n]
        pass
    return weights

def main(argv):
    read(argv[1])
    # weights = primal_svm(100, 700/873, 0.000001)
    weights = dual_svm(100/873)
    print(weights)
    print("training error " + str(test(weights)))
    read(argv[2])
    print("testing error " + str(test(weights)))
    pass

if __name__ == "__main__":
    argv = ["svm.py", "SVM/train.csv", "SVM/test.csv"]
    main(argv)