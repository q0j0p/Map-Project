#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 19:13:56 2016

@author: User1

# Audit street names: survey street name endings 
# Map nomenclature variants in a dictionary ('mapping')
"""
OSMFILE = 'sample.osm'
from collections import defaultdict
import re 
import xml.etree.cElementTree as ET

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Highway", "Loop", "Mall", "Terrace", "Parkway", "Circle", "Way", "Center"]


mapping = { "St": "Street",
            "St.": "Street", 
            "Ave": "Avenue", 
           "AVE" : "Avenue", 
            "Rd.": "Road", 
           "Rd" : "Road", 
           "Blvd": "Boulevard", 
           "Hwy" : "Highway", 
           "Pkwy" : "Parkway", 
           "highway" : "Highway"
           
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    count = 0
    # parses osm file, 
    #finds "tag" or "way" elements 
    #if k attibute indicates enclosing element tag is street address, 
    #evaluates tag attribute value (which is street name string)
    #
#    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osmfile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    
                    audit_street_type(street_types, tag.attrib['v'])
#                    print tag.attrib['v']
                    count += 1 
#    osm_file.close()
#    print "street types", street_types
    print 'street count is:', count
    return street_types


def update_name(name, mapping):
    
#    print 'name is:',name.split(' ')[-1], 'mapping is ', mapping
    wordlist = name.split(' ')
    lastbit = wordlist[-1]
    lastlen = len(lastbit)
    rest = name[:-lastlen]
    m = re.search(r'\S{1,4}\.?$', lastbit) 
#    print 'lastbit:',lastbit, m.group()
#    street_types[m.group()].add(name)
    if m.group() in mapping.keys(): 
        name = rest + mapping[m.group()]
#        mapping[lastbit] = mapping[m.group()] 
    
    else: 
        for ex in expected: 
            if unicode(ex.lower) == unicode(lastbit): 
                name = rest + ex 
            elif ex[0].lower ==lastbit[0].lower and (ex[1] == lastbit[1] or lastbit[1] == ex[-1]):
                name = rest + ex
            elif lastbit == 'highway': 
                name = rest + mapping[lastbit]
#                print name

#                mapping[lastbit] = ex 
                
#        for a in 
#    print "mapping:",mapping
    return name

if __name__ == "__main__": 
    print "hi"
    st_types = audit(OSMFILE)
    # pprint.pprint(dict(st_types))
    
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
    print 'corrected name count is:', len(st_types.items())
    
        
