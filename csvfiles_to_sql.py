#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 20:03:47 2016

@author: User1
"""

# Create sql table with schema provided. 

import sqlite3 
DBFILE = "SofHawaii"

#with sqlite3.connect(DBFILE) as db: 
#    cursor = db.cursor()

# create dictionary of queries, one for each table needed in database, directly matching sql schema  
QUERY = {
    'nodes':
        '''CREATE TABLE nodes (
        id INTEGER PRIMARY KEY NOT NULL,
        lat REAL,
        lon REAL,
        user TEXT,
        uid INTEGER,
        version INTEGER,
        changeset INTEGER,
        timestamp TEXT );''' ,
    'nodes_tags':    
        '''CREATE TABLE nodes_tags (
        id INTEGER,
        key TEXT,
        value TEXT,
        type TEXT,
        FOREIGN KEY (id) REFERENCES nodes(id) ); ''', 
    'ways':    
        '''CREATE TABLE ways (
        id INTEGER PRIMARY KEY NOT NULL,
        user TEXT,
        uid INTEGER,
        version TEXT,
        changeset INTEGER,
        timestamp TEXT ); ''', 
    'ways_tags':    
        '''CREATE TABLE ways_tags (
        id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        type TEXT,
        FOREIGN KEY (id) REFERENCES ways(id) ); ''', 
    'ways_nodes':
        '''CREATE TABLE ways_nodes (
        id INTEGER NOT NULL,
        node_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        FOREIGN KEY (id) REFERENCES ways(id),
        FOREIGN KEY (node_id) REFERENCES nodes(id)
        );'''
}


# 'Helper files for data import to database
import csv 
from pprint import pprint
import io
import codecs

# change unicode bytestrings to utf-8
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")
class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self
        
        
        
        
# Next iteration: node_tags.csv to node_tags table 
# create a function to transfer data from .csv to sql database table
## extract rows of data from .csv to tuples, rendering all values into unicode 

def csv_to_tuple(csvfile):
    with open(csvfile,'rb') as csvf: 
        csvReader = UnicodeReader(csvf)
        csvd = [tuple(a1) for a1 in csvReader]
        header = csvd[0]
        print 'csv file header: ', header
        return csvd

# takes list of tuples (tlist, extracted from .csv) and inserts into sql table in database
def tuples_to_table(tlist, table, db): 
    db1 = sqlite3.connect(db)
    cursor1 = db1.cursor()    
    vname_ = tuple(a.encode('utf-8') for a in tlist[0]) # sql variable name must be a tuple in UTF_8 encoding
    print 'table columns: ', vname_
    cursor1.executemany(
    '''INSERT INTO {}{} VALUES ({}?);'''.format(table, 
                                                 vname_, 
                                                 '?,'*(len(tlist[0])-1)), 
        tlist[1:])
    db1.commit() 
    db1.close()

    
# Next iteration: ways.csv to ways table 
# create function that takes data from .csv to table from start to finish  

def csv_to_table(csvfile, table, dbfile): 
    
    tdata = csv_to_tuple(csvfile) 
#    print 'tdata[:2]', tdata[:2]
    tuples_to_table(tdata, table, dbfile)    

#csv_to_table(CSVFILE, TABLE, DBFILE)


# Next iteration: ways_tags to database 
# Create function that creates database and necessary tables, takes data from .csv file to table  

def csv_to_sql(csvfile, table, database, sqlquery): 
    db = sqlite3.connect(database)
    cursor = db.cursor()
    
    # See if table exists: if true, drop and create new
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(table))  
    rows = cursor.fetchall() 
    if rows: 
        cursor.execute("DROP TABLE {}".format(table))
        print "table dropped:", cursor.fetchall()
    print 'Creating table', table
    cursor.execute(sqlquery)    
    db.commit()

    # Transfer data from .csv to table
    csv_to_table(csvfile, table, database)
    print 'final call:', cursor.fetchall()
    db.close()

#csv_to_table(CSVFILE, TABLE, DBFILE) 

# Create database tables.

# DBFILE = "SofHawaii" 
CSVFILES = ['nodes.csv', 'nodes_tags.csv', 'ways.csv', 'ways_nodes.csv', 'ways_tags.csv']
DBTABLES = ['nodes', 'nodes_tags', 'ways', 'ways_nodes', 'ways_tags']
QUERY = QUERY

for n, csvfile in enumerate(CSVFILES): 
    table = DBTABLES[n]
    csv_to_sql(csvfile, table, DBFILE, QUERY[table])