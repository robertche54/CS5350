import sqlite3 as sl
import statistics
import math
import re
import random

con = sl.connect(':memory:')
# The name of each column
attributes = []
# The columns that need to be split with median value
to_process = []
# List of medians for columns that need to be processed
medians = {}
# Most frequent value in each column
modes = {}

# Holds the list of stumps
stumps = []
# List of weights that uses sql id as index
weights = []

# Returns if string s is an integer
def IsInt(s):
    return re.match(r"[-+]?\d+(\.0*)?$", s) is not None

# Stump class that is a depth 1 tree
class Stump():
    
    # Pivot is the column
    # Classifier is the label that the column is split to find
    def __init__(self, pivot, classifier):
        self.thresholds = {}
        self.pivot = pivot
        self.classifier = classifier
        self.total_error = 0
        
        # Gets all attributes for the column
        values = con.execute("SELECT DISTINCT " + pivot + " FROM data").fetchall()
        label = attributes[len(attributes)-1]

        # For every attribute
        for value in values:

            # This is unbelievably stupid
            limit = "WHERE " + pivot + " = '" + value[0] + "'"
            yes_limit = " AND " + label + " = '" + classifier + "'"
            no_limit = " AND " + label + " != '" + classifier + "'"

            count = {"yes" : 0, "no" : 0}
            for pair in con.execute("SELECT id FROM data " + limit + yes_limit).fetchall():
                count["yes"] += weights[int(pair[0])-1]
            for pair in con.execute("SELECT id FROM data " + limit + no_limit).fetchall():
                count["no"] += weights[int(pair[0])-1]

            # Finds number of rows where the (pivot) column is equal to the attribute for label
            # yes = con.execute("SELECT COUNT(*) FROM data " + limit + yes_limit).fetchall()[0][0]
            # no = con.execute("SELECT COUNT(*) FROM data " + limit + no_limit).fetchall()[0][0]

            # print(value[0] + " " + str(yes) + " " + str(no))

            # If the leaf node predicts the label
            if count["yes"] >= count["no"]:
               self.thresholds[value[0]] = 1
               # The error will be the rows that don't return the prediction, aka opposite
               self.total_error += count["no"]
               #self.total_error += self.weighted_error(limit + no_limit)
               # print(self.pivot + " error: " + limit + " = " + str(self.weighted_error(limit + no_limit)))
            else:
               self.thresholds[value[0]] = -1
               self.total_error += count["yes"]
               #self.total_error += self.weighted_error(limit + yes_limit)
               # print(self.pivot + " error: " + limit + " = " + str(self.weighted_error(limit + no_limit)))
            pass

        #if self.total_error == 0:
        #    if (len(stumps) == 0):
        #        self.weight = 1
        #    else:
        #        self.weight = stumps[len(stumps)-1].weight
        #else:
        #print(self.pivot + " " + str(self.total_error))
        self.weight = 0.5 * math.log((1 - self.total_error)/self.total_error)
        pass

    #def weighted_error(self, limit):
    #    error = 0
    #    ids = con.execute("SELECT id FROM data " + limit).fetchall()
    #    for id in ids:
    #        #print(limit + "    " + str(id) + " " + str(weights[int(id[0])-1]))
    #        error += weights[int(id[0])-1]
    #    return error

    def evaluate(self, values):
        return self.weight * self.thresholds[values[self.pivot]]

    pass

def init_sql(filename):
    global attributes
    with open("EnsembleLearning/" + filename, 'r') as f:
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
    # print(threshold)
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
            trim = []
            for value in values:
                trim.append(int(value[0]))
            median = str(statistics.median(trim))
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

def total_weights():
    total = 0
    for weight in weights:
        total += weight
    return total

# This finds the total entropy for a specific column
def weighted_entropy(column, classifier):
    label = attributes[len(attributes)-1]
    total = total_weights()
    entropy = 0
    # every attribute in the column
    values = con.execute("SELECT DISTINCT " + column + " FROM data").fetchall()
    for value in values:
        counts = {"total" : 0, "yes" : 0, "no" : 0}
        # Finds ever row where the column = the attribute
		# row[0] is the id, which is used for the index of the weight list
		# row[1] is the label which is either yes or no
        data = con.execute("SELECT id, " + label + " FROM data WHERE " + column + " = '" + value[0] + "'").fetchall()
        for row in data:
            # total additive weights
            counts["total"] += weights[row[0]-1]
            if row[1] == classifier:
                # amount of label = yes
                counts["yes"] += weights[row[0]-1]
            else:
                # amount of label = no
                counts["no"] += weights[row[0]-1]
            pass
        yes = counts["yes"]/counts["total"]
        no = counts["no"]/counts["total"]
        # entropy = (Sv/1) * (+p * ln(+p) + -p ln(-p)
        entropy -= (counts["total"]/total) * (yes * math.log(yes) + no * math.log(no))
        pass
    # print(column + " " + str(entropy))
    return entropy
    pass

# finds the best stump by highest weight
def next_best_stump(classifier):
    best_stump = Stump(attributes[0], classifier)
    for i in range(len(attributes)-1):
        next_stump = Stump(attributes[i], classifier)
        #if len(stumps) == 1:
        #    print(next_stump.pivot + " " + str(next_stump.total_error))
        if (abs(next_stump.weight) > abs(best_stump.weight)):
            best_stump = next_stump
        pass
    return best_stump

# finds the best stump based on fractional, weighted information gain (entropy)
def best_gain_stump(classifier):
    best_attribute = attributes[0]
    entropy = weighted_entropy(best_attribute, classifier)
    for i in range(len(attributes)-1):
        next_entropy = weighted_entropy(attributes[i], classifier)
        if next_entropy < entropy:
            best_attribute = attributes[i]
            entropy = next_entropy
        pass
    # print(best_stump.pivot + " " + str(best_stump.total_error))
    return Stump(best_attribute, classifier)

# for testing purposes
#def bobo_sort(classifier):
#    new_attributes = attributes.copy()
#    # print(attributes[len(attributes)-1])
#    new_attributes.remove(attributes[len(attributes)-1])
#    rand = random.randint(0, len(new_attributes)-1)
#    obviously_the_best_stump = Stump(new_attributes[rand], classifier)
#    new_attributes.remove(new_attributes[rand])
#    while len(new_attributes) > 0 and (obviously_the_best_stump.weight < 0.6):
#        rand = random.randint(0, len(new_attributes)-1)
#        obviously_the_best_stump = Stump(new_attributes[rand], classifier)
#        new_attributes.remove(new_attributes[rand])
#    return obviously_the_best_stump

def calculate_new_weights(stump, classifier):
    label = attributes[len(attributes)-1]
    total = 0
    values = con.execute("SELECT id, " + stump.pivot + ", " + label + " FROM data").fetchall()
    for value in values:
        # Sample is correctly identified, (yi = h(xi))
        if (stump.thresholds[value[1]] == 1 and value[2] == classifier) or (stump.thresholds[value[1]] == -1 and value[2] != classifier):
            # multiply dt with e^-a
            weights[value[0]-1] *= math.exp(-stump.weight)
        else:
            # multiply dt with e^a
            weights[value[0]-1] *= math.exp(stump.weight)
        total += weights[value[0]-1]
        pass

    # normalize all weights to 1
    for i in range(len(weights)):
        weights[i] /= total

    #x = 0
    #for i in range(len(weights)):
    #    x += weights[i]
    #print(x)
    pass

def learn(max_depth, classifier):
    global stumps
    global weights

    # Clears stumps and weights
    stumps = []
    weights = []

    # Update each weight to be 1/# of rows
    total = con.execute("SELECT COUNT(*) FROM data").fetchall()[0][0]
    for i in range(total):
        weights.append(float(1/total))
        pass

    #print("weights before : " + str(weights))

    for i in range(max_depth):
        #stump = best_gain_stump(classifier)
        stump = next_best_stump(classifier)
        #print("median chosen for patient weight: " + medians[2])
        #print("stump chosen: " + stump.pivot + " " + str(stump.weight) + " " + str(stump.total_error))
        calculate_new_weights(stump, classifier)
        #print("weights after : " + str(weights))
        #print(stump.pivot + " " + str(stump.total_error))
        stumps.append(stump)
    pass

def main():

    init_sql("train.csv")
    read("train.csv")
    post_process()

    #learn(10 , "yes")
    #print(predict("dummy_test.csv"))
        
    for i in range(1, 501):
        learn(i , "yes")
        print(str(i) + ", " + str(predict("train.csv")) + ", " + str(predict("test.csv")))

    # for stump in stumps:
    #    print(stump.pivot + ", " + str(stump.weight) + ", " + str(stump.total_error))
    # pass

main()