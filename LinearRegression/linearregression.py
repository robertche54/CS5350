import math
import random

data = []

def read(filename):
    with open ("LinearRegression/" + filename, 'r') as f:
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
    gradients = [0] * (y+1)
    for t in range(len(data)):
        # Finds lms cost
        wx = weights[y]
        for i in range(y):
            wx += weights[i]*data[t][i]
            pass
        cost = data[t][y] - wx
        # Finds gradients per column by multiplying cost with value in data at column
        gradients[y] -= cost
        for i in range(y):
            gradients[i] -= cost * data[t][i]
            pass
        pass
    return gradients
    pass

def gradient_descent(iterations, r, weights = None):
    # initialize weight at 0 and r at 1
    if weights is None:
        weights = [0] * len(data[0])
    prev_cost = 0
    while iterations != 0:
        new_weights = lms_gradients(weights)
        # Find normalization of vector weight difference
        # ||w_t - w_(t-1)||
        # norm = 0
        for i in range(len(weights)):
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
        weights = [0] * len(data[0])
    prev_cost = 0
    while iterations != 0:
        # Get random training sample
        t = random.randint(0, len(data)-1)
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
        print("cost : " + str(cost))
        # If iteration count is reached or cost function has converged past tolerance level
        if abs(cost - prev_cost) < math.pow(10, -6):
            return weights
        prev_cost = cost
        pass
        iterations -= 1
        pass
    return weights
    pass

def test(weights):
    y = len(data[0])-1
    cost = 0
    for line in data:
        wx = weights[y]
        for i in range(y):
            wx += weights[i]*line[i]
            pass
        cost += math.pow(line[y] - wx, 2)
        pass
    return 0.5 * cost
    pass

def solve_math():
    # Data is a size d x m matrix
    y = len(data[0])

    # Finds (X^T * X)^-1
    # Will be size d x d
    # gramian = []
    gramian = [[1/(sum(a*b for a,b in zip(row[:-1], column[:-1]))) for column in data] for row in data]
    # for t in range(len(data)):
        # A matrix times its self transposed will just be its row multiplied by every row
    #     row = []
    #     for x in range(len(data)):
    #         element = 0
    #         for i in range(y):
    #             element += data[t][i] * data[x][i]
    #             pass
    #         # Add inverse to the new matrix
    #         row.append(1/element)
    #         pass
    #     gramian.append(row)
    #     pass

    # xy = []
    # Finds XY where y is size m x 1
    # Will be size d x 1
    for t in range(len(data)):

        pass

    pass

def main():
    
    # read("train.csv")
    # weights = gradient_descent(-1, 0.0078125)
    # print("weights : " + str(weights))
    # read("test.csv")
    # print("testing cost : " + str(test(weights)))

    # read("train.csv")
    # weights = stochastic_descent(-1, 0.015625)
    # print("weights : " + str(weights))
    # read("test.csv")
    # print("testing cost : " + str(test(weights)))

    read("train.csv")
    solve_math()

    pass

main()
