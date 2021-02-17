import sqlite3 as sl
import math
from queue import PriorityQueue

con = sl.connect(':memory:')
columns = []

def init_sql(filename):
    global columns
    with open("DecisionTree/" + filename, 'r') as f:
        line = f.readlines()[-1]
        columns = line.split(',')

    values = ""
    for column in columns:
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
            values = ', '.join(columns)[:-1]
            params = ['?' for item in terms]
            con.execute("INSERT INTO data (" + values + ") VALUES (%s)" % ','.join(params), terms)
            pass

def entropy(limit):
    column = columns[len(columns)-1]
    i = 0

    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM data " + limit + "GROUP BY " + column + " order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from data " + limit).fetchall()[0][0]
    for pair in values:
        ratio = pair[1]/total
        i -= ratio * math.log(ratio)
    return i

def find_optimal_attribute(columns, limits):
    limit = "WHERE"
    if limits:
        for pair in limits:
            # 5 characters are always removed in case limits is empty so 2 spaces are put in front of AND
            limit += " " + pair[0] + "='" + pair[1] + "' AND  "
            # limit = limit[:-5]

    best = PriorityQueue()
    for i in range(len(columns)-1):
        values = con.execute("SELECT " + columns[i] + ", COUNT(*) as [Count] FROM data " 
                             + limit[:-5] + "GROUP BY " + columns[i] + " order by [Count] desc").fetchall()
        total = con.execute("SELECT COUNT(*) from data " + limit[:-5]).fetchall()[0][0]
        loss = 0
        for pair in values:
            loss += (pair[1]/total) * entropy(limit + " " + columns[i] + "='" + pair[0] + "' ")
        best.put((loss, columns[i]))

    return(best.get()[1])

def train():
    print(find_optimal_attribute(columns, []))
    # make tree based off that attribute
    # remove that attribute from the attribute pool
    # for each split in tree
    # find optimal attribute
    # limit that split

def main():
    init_sql("data-desc.txt")
    read("train.csv")
    train()

main()