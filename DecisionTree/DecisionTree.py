import csv

def read():
    with open ("DecisionTree/test.csv", 'r') as f:
        for line in f:
            terms = line.strip().split(',')
            print(line)
            pass

def main():
    read()

main()