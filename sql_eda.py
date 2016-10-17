#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 20:27:06 2016

@author: User1
"""
import sqlite3
# 

def do_sql(database, query): 
    db = sqlite3.connect(database)
    c = db.cursor()

    c.execute(query) 
    rows = c.fetchall() 
#    for r in rows: 
#        print r
    db.close()
    return rows