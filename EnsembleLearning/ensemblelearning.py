import sqlite3 as sl
import statistics
import math

con = sl.connect(':memory:')
attributes = []
to_process = []
stumps = []
weights = []
medians = {}
modes = {}

class Stump():
    
    def __init__(self, pivot, classifier):
        self.thresholds = {}
        self.pivot = pivot
        self.classifier = classifier
        self.total_error = 0
        
        values = con.execute("SELECT DISTINCT " + pivot + " FROM data").fetchall()
        label = attributes[len(attributes)-1]
        for value in values:
            limit = "WHERE " + pivot + " = '" + value[0] + "'"

            yes_limit = " AND " + label + " = '" + classifier + "'"
            no_limit = " AND " + label + " != '" + classifier + "'"

            yes = con.execute("SELECT COUNT(*) FROM data " + limit + yes_limit).fetchall()[0][0]
            no = con.execute("SELECT COUNT(*) FROM data " + limit + no_limit).fetchall()[0][0]

            if yes >= no:
               self.thresholds[value[0]] = 1
               self.total_error += self.weighted_error(limit + no_limit)
            else:
               self.thresholds[value[0]] = -1
               self.total_error += self.weighted_error(limit + yes_limit)
            pass

        #if self.total_error == 0:
        #    perfect stump has been found, divide by zero error!

        print(self.total_error)
        self.weight = 0.5 * math.log((1 - self.total_error)/self.total_error)
        pass

    def weighted_error(self, limit):
        error = 0
        ids = con.execute("SELECT id FROM data " + limit).fetchall()
        for id in ids:
            error += weights[int(id[0])-1]
        return error

    def evaluate(self, values):
        return self.weight * self.thresholds[values[self.pivot]]

    pass

def init_sql(filename):
    global attributes
    global to_process
    with open("EnsembleLearning/" + filename, 'r') as f:
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
    pass

def read(filename):
    with open ("EnsembleLearning/" + filename, 'r') as f:
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

def evaluate(sample):
    threshold = 0
    for stump in stumps:
        threshold += stump.evaluate(sample)
    if (threshold >= 0 and stumps[0].classifier == sample[attributes[len(attributes)-1]]) or (threshold < 0 and stumps[0].classifier != sample[attributes[len(attributes)-1]]):
        return 1
    else:
        return 0

def predict(filename):
    data = []

    with open ("EnsembleLearning/" + filename, 'r') as f:
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
        acc += evaluate(sample)
    return acc/len(data)

def post_process():
    global medians
    for i in range(len(attributes)):
        if i in to_process:
            values = con.execute("SELECT " + attributes[i] + " FROM data").fetchall()
            median = str(statistics.median(values)[0])
            medians[i] = median
            con.execute("UPDATE data SET " + attributes[i] + " = CASE WHEN " + attributes[i] + " >= " + median + " THEN 1 ELSE 0 END")
        else:
            most = mode(attributes[i], [])
            modes[i] = most[0]
            con.execute("UPDATE data SET " + attributes[i] + " = '" + most[0] + "' WHERE " + attributes[i] + " = 'unknown'")
        pass

def make_limit(limits):
    limit = "WHERE"
    if limits:
        for pair in limits:
            # 5 characters are always removed in case limits is empty so 2 spaces are put in front of AND
            limit += " " + pair[0] + "='" + pair[1] + "' AND  "
            # limit = limit[:-5]
    return limit

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

def next_best_stump(classifier):
    best_stump = Stump(attributes[0], classifier)
    for i in range(1, len(attributes)-2):
        next_stump = Stump(attributes[i], classifier)
        if (next_stump.total_error < best_stump.total_error):
            best_stump = next_stump
    return best_stump

def calculate_new_weights(stump, classifier):
    label = attributes[len(attributes)-1]
    weight_correct = math.exp(-stump.weight)
    weight_incorrect = math.exp(stump.weight)
    total = 0

    values = con.execute("SELECT id, " + stump.pivot + ", " + label + " FROM data").fetchall()
    for value in values:
        if (stump.thresholds[value[1]] == 1 and value[2] == classifier) or (stump.thresholds[value[1]] == -1 and value[2] != classifier):
            weights[value[0]-1] *= weight_correct
        else:
            weights[value[0]-1] *= weight_incorrect
        total += weights[value[0]-1]

    for i in range(len(weights)):
        weights[i] /= total
    pass

def learn(max_depth, classifier):
    global weights
    global stumps
    stumps = []
    total = con.execute("SELECT COUNT(*) FROM data").fetchall()[0][0]
    for i in range(total):
        weights.append(float(1/total))
        pass

    for i in range(max_depth):
        stump = next_best_stump(classifier)
        stumps.append(stump)
        calculate_new_weights(stump, classifier)

    pass

def main():

    init_sql("bank.csv")
    read("bank.csv")
    post_process()

    learn(10, "yes")

    print(predict("bank.csv"))

    pass

main()