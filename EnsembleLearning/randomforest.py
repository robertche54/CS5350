import sqlite3 as sl
import math
import statistics
import sys 
import re
import random
from queue import PriorityQueue

con = sl.connect(':memory:')
# The name of each column
attributes = []
# The columns that need to be split with median value
to_process = []
# List that holds all the tree roots
trees = []
# Tables at node
tables = []
# List of medians for columns that need to be processed
medians = {}
# Most frequent value in each column
modes = {}

# Returns if string s is an integer
def IsInt(s):
    return re.match(r"[-+]?\d+(\.0*)?$", s) is not None

# Node class for tree
class Node():
    def __init__(self, pivot):
        self.thresholds = {}
        self.pivot = pivot

    def evaluate(self, values):
        piv = values[self.pivot]
        value = self.thresholds[piv]
        if(isinstance(value, Node)):
            return value.evaluate(values)
        else:
            return value

    def add_node(self, key, node):
        self.thresholds[key] = node
    pass

def init_sql(filename):
    global attributes
    with open(filename, 'r') as f:
        line = f.readline()
        attributes = line.split(';')
        line = f.readline()
        terms = line.split(';')
        # Find which integer columns need processing
        for i in range(len(terms)):
            #if not terms[i].startswith('"'):
            if IsInt(terms[i]):
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
        con.execute(""" 
            CREATE TABLE bag ( id,
            """ + values + " ) ")
    pass

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

def post_process():
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
            most = mode(attributes[i], [], "data")
            modes[i] = most[0]
            con.execute("UPDATE data SET " + attributes[i] + " = '" + most[0] + "' WHERE " + attributes[i] + " = 'unknown'")
        pass

def evaluate(sample):
    weights = {"yes" : 0, "no" : 0}
    for tree in trees:
        data = tree.evaluate(sample)
        for pair in tree.evaluate(sample):
            weights[pair] += data[pair]
    if weights["yes"] >= weights ["no"]:
        return "yes"
    else:
        return "no"
    pass

def predict(filename):
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
                elif terms[i] == "unknown":
                    terms[i] = modes[i]
                sample[attributes[i]] = terms[i]
            data.append(sample)
            pass
        pass

    acc = 0
    for sample in data:
        if evaluate(sample) == sample[attributes[len(attributes)-1]]:
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

def entropy(limit, table):
    label = attributes[len(attributes)-1]
    i = 0
    values = con.execute("SELECT " + label + ", COUNT(*) as [Count] FROM " + table + " "
                         + limit + "GROUP BY " + label + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from " + table + " " + limit).fetchall()[0][0]
    for pair in values:
        ratio = pair[1]/total
        i -= ratio * math.log(ratio)
    return i

def count(column, limits, table):
    limit = make_limit(limits)[:-5]
    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM " + table + " "
                         + limit + "GROUP BY " + column + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) FROM " + table + " " + limit).fetchall()[0][0]
    counts = {}
    for pair in values:
        counts[pair[0]] = pair[1]/total
    return counts

def mode(column, limits, table):
    limit = make_limit(limits)[:-5]
    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM data " 
                         + limit + "GROUP BY " + column + " order by [Count] desc").fetchall()
    if (len(values) == 0):
        return (mode(column, [], table)[0], True)
    most = values[0][0]
    largest = values[0][1]
    for pair in values:
        if pair[1] > largest:
            most = pair[0]
            largest = pair[1]
    return (most, len(values) == 1)

def find_optimal_attribute(columns, limits, table):
    limit = make_limit(limits)
    best = PriorityQueue()
    for i in range(len(columns)):
        values = con.execute("SELECT " + columns[i] + ", COUNT(*) as [Count] FROM " + table + " " 
                             + limit[:-5] + "GROUP BY " + columns[i] + " order by [Count] desc").fetchall()
        total = con.execute("SELECT COUNT(*) from " + table + " " + limit[:-5]).fetchall()[0][0]
        loss = 0
        for pair in values:
            loss += (pair[1]/total) * entropy(limit + " " + columns[i] + "='" + pair[0] + "' ", table)
        best.put((loss, columns[i]))
        pass
    return(best.get()[1])

def build_tree(current, columns, limits, samples, depth):
    depth -= 1
    values = con.execute("SELECT DISTINCT " + current.pivot + " FROM data").fetchall()
    # if "unknown" not in values:
    #    values.append("unknown")
    for value in values:
        new_limits = limits.copy()
        new_limits.append((current.pivot, value[0]))
        labels = mode(attributes[len(attributes)-1], new_limits, "samples" + str(abs(depth+1)))
        if labels[1]:
            current.add_node(value[0], { labels[0] : 1 })
        elif depth == 0 or len(columns) == 0:
            current.add_node(value[0], count(attributes[len(attributes)-1], new_limits, "samples" + str(abs(depth+1))))
        else:
            if depth not in tables:
                make_samples(abs(depth), samples)
                tables.append(depth)
            new_columns = columns.copy()
            next = find_optimal_attribute(new_columns, new_limits, "samples" + str(abs(depth)))
            new_columns.remove(next)
            leaf = Node(next)
            build_tree(leaf, new_columns, new_limits, samples, depth)
            current.add_node(value[0], leaf)
        pass

def make_samples(depth, g):
    con.execute("DROP TABLE IF EXISTS samples" + str(depth))
    values = ""
    for i in range(len(attributes)):
        column = attributes[i]
        values += column + " TEXT, "
    values = values[:-2]
    con.execute("CREATE TABLE samples" + str(depth) + " ( id, " + values + " ) ")
    for _ in range(g):
        con.execute("INSERT INTO samples" + str(depth) + " SELECT * FROM bag ORDER BY random() LIMIT 1")
    pass

def make_bag(m, total):
    con.execute("DELETE FROM bag")
    ids = []
    dupes = {}
    for _ in range(m):
        rand = random.randint(1, total)
        if rand in ids:
            if rand in dupes:
                dupes[rand] += 1
            else: 
                dupes[rand] = 1
        else:
            ids.append(rand)
        pass
    # ids = random.choices(range(1, total+1), k = m)
    if (len(ids) > 0):
        con.execute("INSERT INTO bag SELECT * FROM data WHERE id IN (%s)" % ', '.join([str(i) for i in ids]))
    for id in dupes:
        for _ in range(dupes[id]):
            con.execute("INSERT INTO bag SELECT * FROM data where id = '" + str(id) + "'")
    pass

def learn(max_depth, samples, m):
    new_columns = attributes.copy()
    new_columns.pop()

    #Create new table and select random samples m
    total = con.execute("SELECT COUNT(*) FROM data").fetchall()[0][0]
    if m is None:
        m = total

    make_bag(m, total)
    make_samples(max_depth, samples)
    tables.append(max_depth)
    current = find_optimal_attribute(new_columns, [], "samples" + str(abs(max_depth)))
    new_columns.remove(current)
    root = Node(current)
    build_tree(root, new_columns, [], samples, -1)
    trees.append(root)
    tables.clear()
    pass

def test(training_data, testing_data, samples, m, max_size):
    print("size | training    | test (random forest)")
    print("-----------------------------------------")
    # f = open("randomforest " + str(samples) + ".txt", "w+")
    for i in range(max_size):
        learn(i+1, samples, m)
        line = '%-5i' % (i+1) + "| " + '%-12f%-12s' % (predict(training_data), "| " + str(predict(testing_data)))
        print(line)
        # f.write(line + str("\n"))
        # f.flush()
        pass
    # f.close()
    pass

def main(argv):
    init_sql(argv[1])
    read(argv[1])
    post_process()
    m = None
    if (len(argv) == 6):
        m = argv[5]
    test(argv[1], argv[2], argv[3], m, argv[4])

if __name__ == "__main__":
    # argv = ["randomforest.py", "EnsembleLearning/train.csv", "EnsembleLearning/test.csv", 4, 500, 5000]
    main(sys.argv)
    