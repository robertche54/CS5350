import sqlite3 as sl
import math
import statistics
import sys 
from queue import PriorityQueue

con = sl.connect(':memory:')
root = object()
attributes = []
to_process = []
medians = {}
modes = {}

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
    global to_process
    with open(filename, 'r') as f:
        line = f.readline()
        attributes = line.split(';')
        line = f.readline()
        terms = line.split(';')
        # Find which integer columns need processing
        for i in range(len(terms)):
            if not terms[i].startswith('"'):
                to_process.append(i)
        pass

    values = ""
    for i in range(len(attributes)):
        # Strip quotes messing with sql syntax
        column = attributes[i][1:-1]
        # I give up
        if column == "y\"":
            column = "label"
        if column == "default":
            column = "def"
        attributes[i] = column
        values += column + " TEXT, "
    values = values[:-2]

    with con:
        con.execute(""" 
            CREATE TABLE data ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            """ + values + " ) ")

def read(filename):
    with open (filename, 'r') as f:
        # Because first line contains attributes
        next(f)
        for line in f:
            terms = line.strip().split(';')
            # Strip quotes messing with sql syntax
            for i in range(len(terms)):
                if terms[i].startswith('"') and terms[i].endswith('"'):
                    terms[i] = terms[i][1:-1]
            values = ', '.join(attributes)
            params = ['?' for item in terms]
            con.execute("INSERT INTO data (" + values + ") VALUES (%s)" % ','.join(params), terms)
            pass

def post_process(replace_unknown):
    global medians
    for i in range(len(attributes)):
        if i in to_process:
            values = con.execute("SELECT " + attributes[i] + " FROM data").fetchall()
            trim = []
            for value in values:
                trim.append(int(value[0]))
            median = str(statistics.median(trim))
            medians[i] = median
            con.execute("UPDATE data SET " + attributes[i] + " = CASE WHEN " + attributes[i] + " >= " + median + " THEN 1 ELSE 0 END")
        else:
            most = mode(attributes[i], [])
            modes[i] = most[0]
            if replace_unknown:
                con.execute("UPDATE data SET " + attributes[i] + " = '" + most[0] + "' WHERE " + attributes[i] + " = 'unknown'")
        pass

def predict(filename, replace_unknown):
    data = []

    with open (filename, 'r') as f:
        # Because first line contains attributes
        next(f)
        for line in f:
            terms = line.strip().split(';')
            # Strip quotes messing with sql syntax
            for i in range(len(terms)):
                if terms[i].startswith('"') and terms[i].endswith('"'):
                    terms[i] = terms[i][1:-1]
            sample = {}
            for i in range(len(terms)):
                if i in to_process:
                    # Python is a horrible language
                    terms[i] = str(int(terms[i] >= medians[i]))
                elif replace_unknown and terms[i] == "unknown":
                    terms[i] = modes[i]
                sample[attributes[i]] = terms[i]
            data.append(sample)
            pass
        pass

    acc = 0
    for sample in data:
        if root.evaluate(sample) == sample[attributes[len(attributes)-1]]:
            acc += 1
    return acc/len(data)

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

def majority_error(limit):
    label = attributes[len(attributes)-1]
    i = 0
    values = con.execute("SELECT " + label + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + label + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from data " + limit).fetchall()[0][0]
    values.sort(key=lambda x:x[1])
    return values[0][1]/total

def gini_index(limit):
    label = attributes[len(attributes)-1]
    i = 0
    values = con.execute("SELECT " + label + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + label + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from data " + limit).fetchall()[0][0]
    for pair in values:
        i += math.pow(pair[1]/total, 2)
    return 1-i

def mode(column, limits):
    limit = make_limit(limits)[:-5]
    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + column + " order by [Count] desc").fetchall()
    if (len(values) == 0):
        return (mode(column, [])[0], True)
    most = values[0][0]
    largest = values[0][1]
    for pair in values:
        if pair[1] > largest:
            most = pair[0]
            largest = pair[1]
    return (most, len(values) == 1)

def find_optimal_attribute(columns, limits, gain):
    limit = make_limit(limits)
    best = PriorityQueue()
    for i in range(len(columns)):
        values = con.execute("SELECT " + columns[i] + ", COUNT(*) as [Count] FROM data " 
                             + limit[:-5] + "GROUP BY " + columns[i] + " order by [Count] desc").fetchall()
        total = con.execute("SELECT COUNT(*) from data " + limit[:-5]).fetchall()[0][0]
        loss = 0
        for pair in values:
            loss += (pair[1]/total) * eval(gain + "(\"" + limit + " " + columns[i] + "='" + pair[0] + "' " + "\")")
            #loss += (pair[1]/total) * entropy(limit + " " + columns[i] + "='" + pair[0] + "' ")
        best.put((loss, columns[i]))
        pass

    return(best.get()[1])

def build_tree(current, columns, limits, depth, gain):
    depth -= 1
    # print(str(depth) + str(limits))
    values = con.execute("SELECT DISTINCT " + current.pivot + " FROM data").fetchall()
    #+ make_limit(limits)[:-5]
    if "unknown" not in values:
        values.append("unknown")
    for value in values:
        new_limits = limits.copy()
        new_limits.append((current.pivot, value[0]))
        labels = mode(attributes[len(attributes)-1], new_limits)

        if depth == 0 or labels[1] or len(columns) == 0:
            #current.thresholds[value[0]] = labels[0]
            current.add_node(value[0], labels[0])
        else:
            new_columns = columns.copy()
            next = find_optimal_attribute(new_columns, new_limits, gain)
            new_columns.remove(next)
            leaf = Node(next)
            build_tree(leaf, new_columns, new_limits, depth, gain)
            #current.thresholds[value[0]] = leaf
            current.add_node(value[0], leaf)
        pass

def learn(max_depth, gain):
    global root
    new_columns = attributes.copy()
    new_columns.pop()
    current = find_optimal_attribute(new_columns, [], gain)
    new_columns.remove(current)
    root = Node(current)
    build_tree(root, new_columns, [], max_depth, gain)

def test(gain, training_data, testing_data, replace_unknown, max_size):
    print("size | training    | test (" + gain + ")")
    print("-----------------------------------------")
    for i in range (max_size, 0, -1):
        learn(i, gain)
        print('%-5i' % i + "| " + '%-12f%-12s' % (predict(training_data, replace_unknown), "| " + str(predict(testing_data, replace_unknown))))
        #print(" \hline " + str(i) + " & " + str(predict(training_data)) +  " & " + str(predict(testing_data)) + " \\\\")
    print()

def main(argv):

    init_sql(argv[1])
    read(argv[1])
    post_process(argv[4] == "yes")
    test(argv[3], argv[1], argv[2], argv[4] == "yes", int(argv[5]))

    # init_sql("bank.csv")
    # read("bank.csv")
    # post_process(False)

    # test("entropy")
    # test("majority_error")
    # test("gini_index")

if __name__ == "__main__":
    # argv = ["decisiontree.py", "DecisionTree/bank.csv", "DecisionTree/bank-full.csv", "entropy", "yes", "1"]
    main(sys.argv)
    