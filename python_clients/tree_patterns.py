#!/usr/bin/env python
# Basic patterns to output Willow Tree patterns to a simulator or the actual tree

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

#----------------------------------------
# Constants

num_vines = 40
num_lights_per_vine = 34
frames_per_second = 120

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

coordinates = numpy.zeros((num_vines,num_lights_per_vine), dtype=numpy.object)

for item in json.load(open(options.layout)):
	if 'point' in item:
		for vine in range(num_vines):
			for light in range (num_lights_per_vine):
				coordinates[vine][light] = (tuple(item['point']))

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

# Basic function to output to simulator, 1 channel
# Copy this function and replace between the comment blocks below to alter the pattern
def output_simulation_basic(duration):
    while True:
        pixels = []
        for vine in range(num_vines):
            for light in range(num_lights_per_vine):
                # Change starting here for patterns

                seed = random.uniform(0,1)
                color = seed * 255
                rgb = [color,color/2,color/3]
                pixels.append(rgb)

                # End of pattern block

        # Output the lights
        client.put_pixels(pixels, channel = 0)
        time.sleep(1/frames_per_second)

# Basic function to output to tree, 40 channels
# Copy this function and replace between the comment blocks to alter the pattern
def output_tree(duration):
    while True:
        pixels = numpy.zeros((num_vines,num_lights_per_vine), dtype=numpy.object)
        for vine in range(num_vines):
            for light in range(num_lights_per_vine):
                # Change starting here for patterns
                seed = random.uniform(0,1)
                color = seed * 255
                rgb = [color,color/7,color/2]
                pixels[vine][light] = rgb

                # End of pattern block

        # Output the lights
        for channel in range(num_vines):
            client.put_pixels(pixels[channel], channel = channel)
        time.sleep(1/frames_per_second)

# Output to simulation. Uncomment the function calls below to output to the OpenGL simulator
output_simulation_basic(0)

# Output to tree. Uncomment the function calls below to output to the tree
#output_tree(0)