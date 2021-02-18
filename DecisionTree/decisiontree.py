import sqlite3 as sl
import math
from queue import PriorityQueue

con = sl.connect(':memory:')
root = object()
attributes = []

class Node():

    def __init__(self, pivot):
        self.thresholds = {}
        self.pivot = pivot

    def evaluate(self, values):
        value = self.thresholds[values[self.pivot]]
        if(isinstance(value, Node)):
            return value.evaluate(values)
        else:
            return value

    def add_node(self, key, node):
        self.thresholds[key] = node

    pass

def init_sql(filename):
    global attributes
    with open("DecisionTree/" + filename, 'r') as f:
        line = f.readlines()[-1]
        attributes = line.split(',')
        pass

    values = ""
    for column in attributes:
        values += column + " TEXT, "
    values = values[:-2]

    with con:
        con.execute(""" 
            CREATE TABLE data ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            """ + values + " ) ")
        #print(con.execute("DESCRIBE data").fetchall())

def read(filename):
    with open ("DecisionTree/" + filename, 'r') as f:
        for line in f:
            terms = line.strip().split(',')
            values = ', '.join(attributes)[:-1]
            params = ['?' for item in terms]
            con.execute("INSERT INTO data (" + values + ") VALUES (%s)" % ','.join(params), terms)
            pass

def predict(filename):
    data = []
    with open ("DecisionTree/" + filename, 'r') as f:
        for line in f:
            terms = line.strip().split(',')
            sample = {}
            for i in range(len(terms)):
                sample[attributes[i]] = terms[i]
            data.append(sample)
            pass
        pass

    for sample in data:
        print(sample)
        print(root.evaluate(sample))

def make_limit(limits):
    limit = "WHERE"
    if limits:
        for pair in limits:
            # 5 characters are always removed in case limits is empty so 2 spaces are put in front of AND
            limit += " " + pair[0] + "='" + pair[1] + "' AND  "
            # limit = limit[:-5]
    return limit

def entropy(limit):
    label = attributes[len(attributes)-1]
    i = 0
    values = con.execute("SELECT " + label + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + label + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from data " + limit).fetchall()[0][0]
    for pair in values:
        ratio = pair[1]/total
        i -= ratio * math.log(ratio)
    return i

def mode(column, limits):
    limit = make_limit(limits)[:-5]
    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + column + " order by [Count] desc").fetchall()
    mode = values[0][0]
    largest = values[0][1]
    for pair in values:
        if pair[1] > largest:
            mode = pair[0]
    return (mode, len(values) == 1)

def find_optimal_attribute(columns, limits):
    limit = make_limit(limits)
    best = PriorityQueue()
    for i in range(len(columns)):
        values = con.execute("SELECT " + columns[i] + ", COUNT(*) as [Count] FROM data " 
                             + limit[:-5] + "GROUP BY " + columns[i] + " order by [Count] desc").fetchall()
        total = con.execute("SELECT COUNT(*) from data " + limit[:-5]).fetchall()[0][0]
        loss = 0
        for pair in values:
            loss += (pair[1]/total) * entropy(limit + " " + columns[i] + "='" + pair[0] + "' ")
        best.put((loss, columns[i]))
        pass

    return(best.get()[1])

def build_tree(current, columns, limits, depth):
    depth -= 1
    values = con.execute("SELECT DISTINCT " + current.pivot + " FROM data " + make_limit(limits)[:-5]).fetchall()
    for value in values:
        new_limits = limits.copy()
        new_limits.append((current.pivot, value[0]))
        labels = mode(attributes[len(attributes)-1], new_limits)

        if depth == 0 or labels[1]:
            if(value[0] == 'big' and current.pivot == "persons"):
                print(current.pivot)
            #current.thresholds[value[0]] = labels[0]
            current.add_node(value[0], labels[0])
        else:
            new_columns = columns.copy()
            next = find_optimal_attribute(new_columns, new_limits)
            new_columns.remove(next)
            leaf = Node(next)
            build_tree(leaf, new_columns, new_limits, depth)
            #current.thresholds[value[0]] = leaf
            current.add_node(value[0], leaf)

        for n in nodelist:
            if not n.valid():
                print("INVALID")
        pass

def learn(max_depth):
    global root
    new_columns = attributes.copy()
    new_columns.pop()
    current = find_optimal_attribute(new_columns, [])
    new_columns.remove(current)
    root = Node(current)
    build_tree(root, new_columns, [], max_depth)

def main():
    init_sql("data-desc.txt")
    read("train.csv")
    learn(-1)
    predict("test.csv")

main()
    
    