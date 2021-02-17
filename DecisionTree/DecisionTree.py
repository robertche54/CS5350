import sqlite3 as sl
import math

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

def entropy(limits, column):
    i = 0
    limit = ""

    if(limits):
        limit = "WHERE"
        for pair in limits:
            limit += " " + pair[0] + "='" + pair[1] + "' AND"
            limit = limit[:-3]

    values = con.execute("SELECT " + column + ", COUNT(*) as [Count] FROM data " + limit + "GROUP BY " + column + "order by [Count] desc").fetchall()
    total = con.execute("SELECT COUNT(*) from data").fetchall()[0][0]
    for pair in values:
        ratio = pair[1]/total
        i -= ratio * math.log(ratio)
    return i

def find_optimal_attribute(columns):
    for i in range(len(columns)-1):
        print(str(i) + " " + columns[i])
    return 1

def train():
    gain = entropy([], columns[len(columns)-1])

    print(gain)

def main():
    init_sql("data-desc.txt")
    read("train.csv")
    train()

main()