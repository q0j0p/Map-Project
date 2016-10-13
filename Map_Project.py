#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 17:08:17 2016

@author: User1  

Map Project for Hawaii-- work in progress 
"""

# Create 

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 13:13:22 2016

@author: User1
"""



''' The libraries and packages that this project uses.  
Organize later 
'''

OSMFILE = "SofHexK.osm"
DBFILE = "SofHawaii"
# SCHEMA = schema.schema (schema for .csv files)

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
from bs4 import BeautifulSoup
import urllib 
from geopy.geocoders import Nominatim
import csv
import codecs
import re
import cerberus
import schema
import sqlite3 
import io 



'''
# Create sample data file (smaller in size)
# Generates manageabe sample data by aggregating every kth element.  (Code adapted from Udacity.)
'''

SAMPLEFILE = "sample.osm" # output sample file

j = 5 # Get the first j elements 
k = 10 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
# Helper file for 
     context = iter(ET.iterparse(osm_file, events=('start', 'end')))
     _, root = next(context)
     for event, elem in context:
         if event == 'end' and elem.tag in tags:
             yield elem  #`yield` returns a generator (an iterable object, iterating one by one)
             root.clear()

def create_sampledata(osm_file, sample_file):
    with open(sample_file, 'wb') as output:
         output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
         output.write('<osm>\n  ')
         
         #write firt j elements
         for i, element in enumerate(get_element(OSMFILE)):
             if i < j: 
                 output.write(ET.tostring(element, encoding='utf-8'))
                 
         # Write every kth top level element                 
         for i, element in enumerate(get_element(OSMFILE)): 
             if (j <= i) and (i % k == 0):
                 output.write(ET.tostring(element, encoding='utf-8'))
    
         output.write('</osm>')

         
         
''' 
Execute 
'''

create_sampledata(OSMFILE, SAMPLEFILE)
     