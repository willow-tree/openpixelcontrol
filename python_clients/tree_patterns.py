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
import math
from colorutils import Color

#----------------------------------------
# Constants
num_vines = 40
num_lights_per_vine = 34
frames_per_second = 120
num_vines_per_branch = 5
total_num_lights = num_vines*num_lights_per_vine

# RGB default colors for diagnostics
red = Color((255, 0, 0))
green = Color((0, 255, 0))
blue = Color((0, 0, 255))
gold = Color((255, 223, 0))
orchid = Color((148, 0, 211))
diagnostic_colors = [red, green, blue, gold, orchid]

#----------------------------------------
# Common helper methods
def output_to_tree(pixels):
    for channel in range(num_vines):
        client.put_pixels(pixels[channel,:].ravel(), channel = channel)
    time.sleep(1/frames_per_second) 

def output_to_simulation(pixels):
    client.put_pixels(pixels, channel = 0)
    time.sleep(1/frames_per_second)

def initialize_tree_pixels():
    return numpy.zeros((num_vines,num_lights_per_vine), dtype=numpy.object)

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
        vine_index = int(index/num_lights_per_vine)
        light_index = index%num_lights_per_vine  
        coordinates[vine_index][light_index] = (tuple(item['point']))

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
# Diagnostic patterns

# Basic function to output diagnostic pattern to simulator, 1 channel
# Copy this function and replace between the comment blocks below to alter the pattern
def output_diagnostic_simulation(duration):
    while True:
        pixels = []
        for vine in range(num_vines):
            for light in range(num_lights_per_vine):            
                # Change starting here for patterns
                # Diagnostic pattern displays 5 different colors per branch (each vine is a different color),
                # replicated across all 8 branches.
                pixels.append(diagnostic_colors[vine%num_vines_per_branch])

        # Output the lights
        output_to_simulation(pixels)

# Basic function to diagnostic pattern to tree, 40 channels
# Copy this function and replace between the comment blocks to alter the pattern
def output_diagnostic_tree(duration):
    while True:
        pixels = initialize_tree_pixels()
        for index in range(total_num_lights):
            vine_index = int(index/num_lights_per_vine)
            light_index = index%num_lights_per_vine  

            # Change starting here for patterns
            # Diagnostic pattern displays 5 different colors per branch (each vine is a different color),
            # replicated across all 8 branches.
            pixels[vine_index][light_index] = diagnostic_colors[vine_index%num_vines_per_branch]
            # End of pattern block

        # Output the lights
        output_to_tree(pixels)
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
    random_values = [random.random() for ii in range(total_num_lights)]
    start_time = time.time()
    pixels = []

    while True:
        t = time.time() - start_time
        pixels = [lava_lamp_pixel_color(t*0.6, coord, ii, total_num_lights, random_values) for ii, coord in enumerate(coordinates.flat)]
        output_to_simulation(pixels)

def lava_lamp_pattern_tree():
    random_values = [random.random() for ii in range(total_num_lights)]
    start_time = time.time()
    pixels = initialize_tree_pixels()

    while True:
        t = time.time() - start_time
        for index, coord in enumerate(coordinates.flat):
            vine_index = int(index/num_lights_per_vine)
            light_index = index%num_lights_per_vine 
            pixels[vine_index][light_index] = lava_lamp_pixel_color(t*0.6, coord, index, total_num_lights, random_values)
        output_to_tree(pixels)
#----------------------------------------------
# Raver plaid
def raver_plaid_tree():
    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 30
    freq_g = 30
    freq_b = 30

    # how many seconds the color sine waves take to shift through a complete cycle
    speed_r = 7
    speed_g = -13
    speed_b = 19

    start_time = time.time()
    sub_lights_num = num_lights_per_vine*num_vines_per_branch*2
    while True:
        pixels = []
        t = time.time() - start_time
        for index in range(4):
            sub_pixels = []

            for ii in range(sub_lights_num):
                pct = ii / sub_lights_num
                # diagonal black stripes
                pct_jittered = (pct * 77) % 37
                blackstripes = color_utils.cos(pct_jittered, offset=t*0.05, period=1, minn=-1.5, maxx=1.5)
                blackstripes_offset = color_utils.cos(t, offset=0.9, period=60, minn=-0.5, maxx=3)
                blackstripes = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)
                # 3 sine waves for r, g, b which are out of sync with each other
                r = blackstripes * color_utils.remap(math.cos((t/speed_r + pct*freq_r)*math.pi*2), -1, 1, 0, 256)
                g = blackstripes * color_utils.remap(math.cos((t/speed_g + pct*freq_g)*math.pi*2), -1, 1, 0, 256)
                b = blackstripes * color_utils.remap(math.cos((t/speed_b + pct*freq_b)*math.pi*2), -1, 1, 0, 256)
                sub_pixels.append((r, g, b))
            
            current_pixels_size = len(pixels)
            current_sub_pixel_size = len(sub_pixels)

            sub_first_half = sub_pixels[:int(current_sub_pixel_size/2)]
            sub_second_half = sub_pixels[int(current_sub_pixel_size/2):]

            for x in sub_first_half:
                pixels.insert(int(current_pixels_size/2), x)
            pixels.extend(sub_second_half)
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / frames_per_second)

# Output to simulation. Uncomment the function calls below to output to the OpenGL simulator
#output_diagnostic_simulation(0)
#lava_lamp_pattern_simulation()
raver_plaid_tree()

# Output to tree. Uncomment the function calls below to output to the tree
#output_diagnostic_tree(0)
#lava_lamp_pattern_tree()