import numpy as np
import pandas as pd
import math
import sys

def sig(s):
    for i in range(len(s)):
        s[i] = 1/(1 + math.exp(-s[i]))
    return s

def p_sig(s):
    for i in range(len(s)):
        s[i] = s[i] * (1 - s[i])
    return s

class NeuralNet():

    def __init__(self, width, data_size = 4, gamma = 0.00001, d = 1):
        self.gamma = gamma
        self.d = d
        self.w1 = np.random.rand(data_size, width)
        self.w2 = np.random.rand(width, 1)
        # self.w1 = np.zeros((data_size, width))
        # self.w2 = np.zeros((width, 1))
        pass

    def evalulate(self, table):
        acc = 0
        for line in table:
            self.y = line.pop()
            self.x = np.asarray(line)
            self.predict()
            if (self.output - self.y >= 0):
                acc += 1
            pass
        return acc/len(table)

    def fit(self, table):
        epochs = 0
        for line in table:
            self.y = line.pop()
            self.x = np.asarray(line)
            self.predict()
            self.backprop(epochs)
            epochs += 1
            pass
        pass

    def predict(self):
        self.n1 = sig(np.dot(self.x, self.w1))
        self.output = np.dot(self.n1, self.w2)
        pass
    
    def backprop(self, t = 0):
        y = (self.y - self.output)
        p_w2 = np.zeros_like(self.w2)
        for i in range(self.w2.shape[0]):
            p_w2[i] = self.n1[i] * y
        p_w1 = np.zeros_like(self.w1)
        # p_w1 = np.dot(self.x.T, self.w2 * dL * p_sig(self.n1))
        for i in range(self.w1.shape[0]):
            for j in range(self.w1.shape[1]):
                p_w1[i][j] = self.w2[j] * self.x[i] * p_sig([self.n1[j]]) 
                pass

        r = self.gamma/(1 + (self.gamma/self.d) * t)
        self.w2 += r * p_w2
        self.w1 += r * p_w1
        pass

    pass

def main(argv):
    classifier = NeuralNet(argv[3])
    testing_data = pd.read_csv(argv[1], header = None).values.tolist()
    training_data = pd.read_csv(argv[2], header = None).values.tolist()
    classifier.fit(testing_data)
    testing_data = pd.read_csv(argv[1], header = None).values.tolist()
    print("width, training error, testing error")
    print(str(argv[3]) + ", " + str(classifier.evalulate(testing_data)) + ", "
          + str(classifier.evalulate(training_data)))
    #print(str(argv[3]) + " & " + str(classifier.evalulate(testing_data)) + " & "
    #      + str(classifier.evalulate(training_data)) + "\\\\ \\hline")
    pass

if __name__ == "__main__":
    #for i in [5, 10, 25, 50, 100]:
    #    argv = ["nn.py","NeuralNetworks/train.csv","NeuralNetworks/test.csv", i]
    #    main(argv)
    main(sys.argv)