import math

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
        gradients[y] += cost
        for i in range(y):
            gradients[i] -= cost * data[t][i]
        pass
    return gradients
    pass

def gradient_descent(iterations):
    # initialize weight at 0 and r at 1
    weights = [0] * len(data[0])
    r = 1
    while iterations != 0:
        new_weights = lms_gradients(weights)
        # Find normalization of vector weight difference
        # ||w_t - w_(t-1)||
        norm = 0
        for i in len(weights):
            weights[i] -= r * new_weights[i]
            norm += math.pow((weights[i] - new_weights[i]), 2)
            pass
        # If norm less than tolerance level then return early
        norm = math.sqrt(norm)
        if norm < math.pow(10, -6):
            print(r)
            return weights
        r /= 2
        iterations -= 1
        pass
    print(r)
    return weights
    pass

def stochastic_descent(iterations, r):
    y = len(data[0])-1
    weights = [0] * len(data[0])

    for t in range(len(data)):
        # Find lms cost for a row 
        wx = weights[y]
        for i in range(y):
            wx += weights[i]*data[t][i]
            pass
        cost = data[t][y] - wx
        # Update weight vector
        for i in range(y):
            weights[i] += r*cost*data[t][i]
            pass
        # If iteration count is reached or cost function has converged past tolerance level
        if t == iterations or cost < math.pow(10, -6):
            return weights
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
        cost += line[y] - wx
        pass
    return cost
    pass

def main():
    read("train.csv")
    weights = learn(-1)

    pass

main()
