#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 17:14:53 2016

@author: User1

Execute script to scrape all conventionally used map features in OSM projects, from wiki 
wikisite = 'http://wiki.openstreetmap.org/wiki/Map_Features'
"""

from bs4 import BeautifulSoup
import urllib 

# access the site and obtain BS object 
wikisite = 'http://wiki.openstreetmap.org/wiki/Map_Features'
r = urllib.urlopen(wikisite).read() 
soup = BeautifulSoup(r, 'html.parser')

# Find all the wiki tables.  
tables = soup.find_all("table", class_='wikitable')

len(tables)
# Map features is listed in 29 tables 

# list of key values that are physical map features 
keys = [table.a['href'] for table in tables]
rows = soup.find_all('tr')

features = []

for n, a1 in enumerate(rows): 
    a2 = a1.find_all('td')
    try:
        if a2[0].a['href'] in keys and a2[1].a['title']: 
                values = a2[1].a['title'].split(':')[1]
                if "(page does not exist)" not in values: 
                    features.append(values)                
    except: 
        pass
 

        
# Find the elements with the 'key' values, 'values' values that correspond to an osm map feature.  
# Count the occurence of each map feature.  

from collections import defaultdict 
import xml.etree.cElementTree as ET


key_tally = defaultdict(set)
value_tally = defaultdict(set) 
feature_tally = defaultdict(set)

for a in features: 
    key_tally[a.split('=')[0]]=0
    value_tally[a.split('=')[1]]=0
    feature_tally[a] = 0
    
def key_type(element, tally):
    for a in tally: 
        if element.attrib['k'] == a: 
            tally[a] +=  1              
    return tally

def value_type(element, tally): 
    for a in tally: 
        a1 = a.split('=')
        if element.attrib['k'] == a1[0] and element.attrib['v'] == a1[1]: 
            tally[a] += 1 
    return tally

def process_attrib(filename, tally, attrib):
    for _, element in ET.iterparse(filename):
        if element.tag == "tag": 
            if attrib == 'k':
                tally = key_type(element, tally)
            elif attrib == 'v': 
                tally = value_type(element, tally)
                
    for a in tally: 
        if tally[a] != 0: 
            tally[a] = tally[a]
    return tally


    
