data = []

def read(filename):
    with open ("EnsembleLearning/" + filename, 'r') as f:
        for line in f:
            terms = line.split(',')
            row = []
            for term in terms:
                row.append(float(term))
                pass
            pass
        pass
    pass

def learn():
    

def main():
    read("train.csv")

    pass

main()
