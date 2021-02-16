import sqlite3 as sl

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
            """ + values + " ); ")
        #print(con.cursor().execute("DESCRIBE data").fetchall())

def read(filename):
    with open ("DecisionTree/" + filename, 'r') as f:
        for line in f:
            terms = line.strip().split(',')
            values = ', '.join(columns)[:-1]
            params = ['?' for item in terms]
            con.execute("INSERT INTO data (" + values + ") VALUES (%s);" % ','.join(params), terms)
            pass

def main():
    init_sql("data-desc.txt")
    read("train.csv")

main()