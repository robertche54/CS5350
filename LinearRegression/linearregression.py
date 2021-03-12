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
    pass

def lms_gradients(weights):
    y = len(data[0])-1
    gradients = [0] * y
    for t in range(len(data)):
        # Finds lms cost
        wx = 0 # weights[y]
        for i in range(y):
            wx += weights[i]*data[t][i]
            pass
        cost = data[t][y] - wx
        # Finds gradients per column by multiplying cost with value in data at column
        # gradients[y] -= cost
        for i in range(y):
            gradients[i] -= cost * data[t][i]
            pass
        pass
    return gradients
    pass

def gradient_descent(iterations, r, weights = None):
    y = len(data[0])-1
    # initialize weight at 0 and r at 1
    if weights is None:
        weights = [0] * y
    prev_cost = 0
    while iterations != 0:
        new_weights = lms_gradients(weights)
        # Find normalization of vector weight difference
        # ||w_t - w_(t-1)||
        # norm = 0
        for i in range(y):
           weights[i] -= r * new_weights[i]
        #   norm += math.pow((weights[i] - new_weights[i]), 2)
           pass
        # If norm less than tolerance level then return early
        # norm = math.sqrt(norm)
        # if norm < math.pow(10, -6):
        #     return weights
        # print(norm)
        # print(weights)
        cost = test(weights)
        print("cost : " + str(cost))
        if (abs(cost - prev_cost) < math.pow(10, -6)):
            return weights
        prev_cost = cost
        iterations -= 1
        pass
    return weights
    pass

def stochastic_descent_all(iterations, r, weights = None):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * len(data[0])
    for t in range(len(data)):
        # Find lms cost for a row 
        wx = weights[y]
        for i in range(y):
            wx += weights[i]*data[t][i]
            pass
        cost = data[t][y] - wx
        # Update weight vector
        weights[y] += r*cost
        for i in range(y):
            weights[i] += r*cost*data[t][i]
            pass
        cost = test(weights)
        print(cost)
        # If iteration count is reached or cost function has converged past tolerance level
        if t == iterations or cost < math.pow(10, -6):
            return weights
        pass
    return weights
    pass

def stochastic_descent(iterations, r, weights = None):
    y = len(data[0])-1
    if weights is None:
        weights = [0] * y
    prev_cost = 0
    while iterations != 0:
        # Get random training sample
        t = random.randint(0, len(data)-1)
        # Find lms cost for a row 
        wx = 0 # weights[y]
        for i in range(y):
            wx += weights[i]*data[t][i]
            pass
        cost = data[t][y] - wx
        # Update weight vector
        # weights[y] += r*cost
        for i in range(y):
            weights[i] += r*cost*data[t][i]
            pass
        cost = test(weights)
        print("cost : " + str(cost))
        # If iteration count is reached or cost function has converged past tolerance level
        if abs(cost - prev_cost) < math.pow(10, -6):
            return weights
        prev_cost = cost
        iterations -= 1
        pass
    return weights
    pass

def test(weights):
    y = len(data[0])-1
    cost = 0
    for line in data:
        wx = 0 # weights[y]
        for i in range(y):
            wx += weights[i]*line[i]
            pass
        cost += math.pow(line[y] - wx, 2)
        pass
    return 0.5 * cost
    pass

def solve_math():
    # Data is a size d x m matrix
    y = len(data[0])-1

    # Finds (X^T * X)^-1
    # Will be size d x d
    gramian = [[0] * y for _ in range(y)]
    
    # Finds XY where Y is size m x 1
    # Will be size d x 1
    matrix = [0] * y

    for row in data:
        for i in range(y):
            matrix[i] += row[i]*row[y]
            for t in range(y):
                gramian[i][t] += row[i]*row[t]
    gramian = [[1/element for element in row] for row in gramian]

    # Finds (X^T * X)^-1 * XY
    # Will be size d x 1
    weights = [0] * y
    for t in range(y):
        for i in range(y):
            weights[t] += gramian[t][i] * matrix[i]

    return weights
    pass

def find(testing_data, training_data, mode, i, r):
    weights = []
    read(testing_data)
    if mode == "gradient_descent":
        if r is None:
            r = 0.0078125
        weights = gradient_descent(i, r)
    elif argv[3] == "stochastic_descent":
        if r is None:
            r = 0.015625
        weights = stochastic_descent(i, r)
    else: #elif mode == "solve_math"
        weights = solve_math()
    print("weights : " + str(weights))
    read(training_data)
    print("testing cost : " + str(test(weights)))
    pass

def main(argv):
    r = None
    i = -1
    if len(argv) == 6:
        r = float(argv[5])
        i = int(argv[4])
    find(argv[1], argv[2], argv[3], i, r)
    pass

if __name__ == "__main__":
    #argv = ["linearregression.py", "LinearRegression/train.csv", "LinearRegression/test.csv", "gradient_descent", "-1", "0.0078125"]
    main(sys.argv)