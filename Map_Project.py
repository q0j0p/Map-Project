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
Todo: Learn to organize dependencies later 
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
k = 5 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
# Helper file for 
     context = iter(ET.iterparse(osm_file, events=('start', 'end')))
     _, root = next(context)
     for event, elem in context:
         if event == 'end' and elem.tag in tags:
             yield elem  #`yield` returns a generator (an iterable object, iterating one by one)
             root.clear()


def create_sampledata(osm_file, sample_file):
    ''' 
    # Execute to create sample file 
    create_sampledata(OSMFILE, SAMPLEFILE)
    '''
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
Data Auditing 
'''

def count_tags(filename):
    '''
    # Identify and tally the number of each tag in the OSM XML dataset.  Uses ET.fromstring()-- 
    # get an idea of performance.
    import xml.etree.cElementTree as ET
    import pprint
    from collections import defaultdict
    '''
    with open(filename, 'r') as f:
        data = f.read()
    tree = ET.fromstring(data)
    d1 = {}
    for el in tree.iter('*'): 
        d1[el.tag] = 0 
    for el in tree.iter('*'): 
        d1[el.tag] +=1 
    return d1

'''
Execute to get all tags in file: 
'''
#tags = count_tags(OSMFILE)
#print tags.keys() 


'''
# These are functions used in verifying osm element data 
'''
# view the tags
def view_attribs(tagstring):
    for _, element in ET.iterparse(OSMFILE): 
        if element.tag == tagstring: 
            pprint.pprint(element.attrib)
    
# get the tag
def get_attrib(tagstring):
    for _, element in ET.iterparse(OSMFILE): 
        if element.tag == tagstring: 
            return element.attrib

# get the set of all values of a given keyvalue in a given tag
def get_allof_attrib(tagstring, keystring): 
    attrib_set = set()
    for _, element in ET.iterparse(OSMFILE): 
        if element.tag == tagstring and keystring in element.attrib.keys(): 
            attrib_set.add(element.attrib[keystring])
    return attrib_set

# get the set of all values of a given keyvalue of a given child tag of a tag  
def get_allof_childattrib(tagstring, childtagstring, childkeystring): 
    attrib_set = set() 
    for _, element in ET.iterparse(OSMFILE): 
        if element.tag == tagstring: 
            for a in element.findall(childtagstring): 
                attrib_set.add(a.get(childkeystring))
    return attrib_set
    
    
'''
# Execute to get bounds attribute: 
bounds = get_attrib('bounds')
print bounds
'''

''' 
Using geolocator module to reverse-lookup coordinates: 
# verify location of coordinates using geopy package (https://pypi.python.org/pypi/geopy#downloads)
# from geopy.geocoders import Nominatim

>>> geolocator = Nominatim()
>>> minloc = geolocator.reverse("{},{}".format(bounds['minlat'], bounds['minlon']))
>>> maxloc = geolocator.reverse("{},{}".format(bounds['maxlat'], bounds['maxlon']))
>>> print maxloc
#print minloc # returns TypeError: __str__ returned non-string (type NoneType)-- coordinates unlabeled. 
''' 

''' 
# all 'way' ids: 
>>> way_ids = get_allof_attrib('way','id')

# all 'relation' ids: 
>>> relation_ids = get_allof_attrib('relation', 'id')

# all 'member' ids in 'relation': 
>>> relation_member_refs = get_allof_childattrib('relation', 'member', 'ref')

# etc. 
>>> way_changesets = get_allof_attrib('way', 'changeset')

>>> node_ids = get_allof_attrib('node', 'id')

>>> way_nd_refs = get_allof_childattrib('way', 'nd', 'ref')

>>> node_nd_refs = get_allof_childattrib('node', 'nd', 'ref')
'''



''' 
Audit functions to check membership of tags in elements
''' 
 
# how many of set one is /isn't in set2?
def a_in_b(set1, set2):
    is_in = 0 
    not_in = 0 
    for id in set1: 
        if id not in set2: 
#            print "{} not in {}".format(id, 'way_ids')
            not_in+=1
        elif id in set2: 
#            print "{} in {}".format(id, 'way_ids')
            is_in+=1
    print 'not_in: {}, is_in: {}'.format(not_in, is_in)
    

# get list of those not in set2
def listof_notin(set1, set2):
    is_in = 0 
    not_in = 0 
    notinlist = []
    for id in set1: 
        if id not in set2: 
#            print "{} not in {}".format(id, 'way_ids')
            not_in+=1
            notinlist.append(id)
        elif id in set2: 
#            print "{} in {}".format(id, 'way_ids')
            is_in+=1
    return notinlist
    
    
'''
# Execute to audit tags: 

# e.g. how many of the member id's in 'relation's are in 'way's? 
>>> what_in_what(relation_member_refs, way_ids)

>>> what_in_what(relation_member_refs, node_ids)

>>> what_in_what(relation_member_refs, way_ids.union(node_ids))

>>> listof_notin(relation_member_refs, way_ids.union(node_ids))

>>> what_in_what(way_nd_refs, node_ids) 

>>> nd_refs = get_allof_attrib('nd', 'ref')
>>> print len(set(nd_refs))
'''

'''
# Function to get number of unique users
''' 
def get_value(element, kitem):
    return element.attrib[kitem]

def get_allelement_attrib(kitem):
    k = set()
    for _, element in ET.iterparse(OSMFILE):
        if  kitem in element.attrib.keys():
            k.add(get_value(element, kitem))
    return k

'''
# Execute: 
users = get_allelement_attrib('uid')
len(users)
''' 




