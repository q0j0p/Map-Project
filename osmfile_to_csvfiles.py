#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 19:55:43 2016

@author: User1
"""

'''
Import to .csv (Code adapted from Udacity course exercises)
'''
DBFILE = "sample.osm"
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = DBFILE
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
DB_TABLES = ('nodes','node_tags','ways','way_nodes','way_tags') 
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position'] 

# import re
# import pprint

# shapes elements into a flattened table
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        node_attribs = {
            'id':element.attrib['id'], 
            'user':element.attrib['user'], 
            'uid':element.attrib['uid'], 
            'version': element.attrib['version'],
            'lat': element.attrib['lat'], 
            'lon': element.attrib['lon'], 
            'timestamp': element.attrib['timestamp'], 
            'changeset': element.attrib['changeset']
            } 
        tags = shape_tags(element, tags)
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        way_attribs = {
            'user':element.attrib['user'], 
            'uid':element.attrib['uid'], 
            'version': element.attrib['version'],
            'id': element.attrib['id'], 
            'timestamp': element.attrib['timestamp'], 
            'changeset': element.attrib['changeset']
            } 
        tags = shape_tags(element,tags)
        # way nodes 
        for n, n1 in enumerate(element.iter("nd")): 
            nd1 = { 
                'id': element.attrib['id'], 
                'node_id': n1.attrib['ref'], 
                'position': n
            } 
            way_nodes.append(nd1)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# shapes osm element attributes into a flattened structure
def shape_tags(element, tags): 
        try: 
            for c1 in element.iter("tag"): 
                c2= {}
                c2['id'] = element.attrib['id']
                c3 = c1.attrib['k'].split(':') 

                if len(c3) == 1: 
                    c2['key'] = c1.attrib['k'] 
                    c2['type'] = 'regular' 
                    c2['value'] = c1.attrib['v']
                elif len(c3) == 2: 
                    c2['key'] = c3[1] 
                    c2['type'] = c3[0]
                c2['value'] = c1.attrib['v'] 
 
                if len(c3) == 3: 
                    c2['key'] = str(c3[1]+":"+c3[2])
                    c2['type'] = c3[0]

                tags.append(c2) 
        except: 
            print "error in ", c2

        return tags
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# uses a validator (cerberus) with schema
def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )

# Allows csv module to handle unicode text
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])



