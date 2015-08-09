#!/usr/bin/env python

from __future__ import division
import time
import sys
import optparse
import random
try:
    import json
except ImportError:
    import simplejson as json

import opc
import color_utils
import numpy


#-----------------------------------------------
# command line

parser = optparse.OptionParser()
parser.add_option('-l', '--layout', dest='layout',
                    action='store', type='string',
                    help='layout file')
parser.add_option('-s', '--server', dest='server', default='127.0.0.1:7890',
                    action='store', type='string',
                    help='ip and port of server')
parser.add_option('-f', '--fps', dest='fps', default=20,
                    action='store', type='int',
                    help='frames per second')

options, args = parser.parse_args()

if not options.layout:
    parser.print_help()
    print
    print 'ERROR: you must specify a layout file using --layout'
    print
    sys.exit(1)

#---------------------------------------
# parse the layout file

print
print '    parsing layout file'
print

coordinates = numpy.zeroes((40,34))

for item in json.load(open(options.layout)):
	if 'point' in item:
		for branch in range(0,39)
			for light in range (0,33)
				coordinates[branch][light] = (tuple(item['point']))

#----------------------------------------
# connect to server

client = opc.Client(options.server)
if client.can_connect():
    print '    connected to %s' % options.server
else:
    # can't connect, but keep running in case the server appears later
    print '    WARNING: could not connect to %s' % options.server
print

#----------------------------------------
# pattern output



