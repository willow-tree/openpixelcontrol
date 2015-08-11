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

for index, item in enumerate(json.load(open(options.layout))):
    if 'point' in item:
        coordinates[int(index/num_lights_per_vine)][index%num_lights_per_vine] = (tuple(item['point']))

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
                color = seed * 80
                rgb = [color,color*3,color]
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
                color = seed * 30
                rgb = [color,color*3,color]
                pixels[vine][light] = rgb

                # End of pattern block

        # Output the lights
        for channel in range(num_vines):
            client.put_pixels(pixels[channel], channel = channel)
        time.sleep(1/frames_per_second)

#-------------------------------------------------------------------------------
# Lava lamp color function

def lava_lamp_pixel_color(t, coord, ii, n_pixels, random_values):
    """Compute the color of a given pixel.

    t: time in seconds since the program started.
    ii: which pixel this is, starting at 0
    coord: the (x, y, z) position of the pixel as a tuple
    n_pixels: the total number of pixels
    random_values: a list containing a constant random value for each pixel

    Returns an (r, g, b) tuple in the range 0-255

    """
    # make moving stripes for x, y, and z
    x, y, z = coord
    y += color_utils.cos(x + 0.2*z, offset=0, period=1, minn=0, maxx=0.6)
    z += color_utils.cos(x, offset=0, period=1, minn=0, maxx=0.3)
    x += color_utils.cos(y + z, offset=0, period=1.5, minn=0, maxx=0.2)

    # rotate
    x, y, z = y, z, x

#     # shift some of the pixels to a new xyz location
#     if ii % 17 == 0:
#         x += ((ii*123)%5) / n_pixels * 32.12 + 0.1
#         y += ((ii*137)%5) / n_pixels * 22.23 + 0.1
#         z += ((ii*147)%7) / n_pixels * 44.34 + 0.1

    # make x, y, z -> r, g, b sine waves
    r = color_utils.cos(x, offset=t / 4, period=2, minn=0, maxx=1)
    g = color_utils.cos(y, offset=t / 4, period=2, minn=0, maxx=1)
    b = color_utils.cos(z, offset=t / 4, period=2, minn=0, maxx=1)
    r, g, b = color_utils.contrast((r, g, b), 0.5, 1.5)
#     r, g, b = color_utils.clip_black_by_luminance((r, g, b), 0.5)

#     # shift the color of a few outliers
#     if random_values[ii] < 0.03:
#         r, g, b = b, g, r

    # black out regions
    r2 = color_utils.cos(x, offset=t / 10 + 12.345, period=3, minn=0, maxx=1)
    g2 = color_utils.cos(y, offset=t / 10 + 24.536, period=3, minn=0, maxx=1)
    b2 = color_utils.cos(z, offset=t / 10 + 34.675, period=3, minn=0, maxx=1)
    clampdown = (r2 + g2 + b2)/2
    clampdown = color_utils.remap(clampdown, 0.8, 0.9, 0, 1)
    clampdown = color_utils.clamp(clampdown, 0, 1)
    r *= clampdown
    g *= clampdown
    b *= clampdown

    # color scheme: fade towards blue-and-orange
#     g = (r+b) / 2
    g = g * 0.6 + ((r+b) / 2) * 0.4

    # apply gamma curve
    # only do this on live leds, not in the simulator
    #r, g, b = color_utils.gamma((r, g, b), 2.2)

    return (r*256, g*256, b*256)

def lava_lamp_pattern_simulation():
    n_pixels = num_vines*num_lights_per_vine
    random_values = [random.random() for ii in range(n_pixels)]
    start_time = time.time()
    pixels = []

    while True:
        t = time.time() - start_time
        pixels = [lava_lamp_pixel_color(t*0.6, coord, ii, n_pixels, random_values) for ii, coord in enumerate(coordinates.flat)]
        client.put_pixels(pixels, channel = 0)
        time.sleep(1/frames_per_second)
#----------------------------------------------

# Output to simulation. Uncomment the function calls below to output to the OpenGL simulator
# output_simulation_basic(0)
lava_lamp_pattern_simulation()

# Output to tree. Uncomment the function calls below to output to the tree
#output_tree(0)