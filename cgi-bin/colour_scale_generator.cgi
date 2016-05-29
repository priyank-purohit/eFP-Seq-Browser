#!/usr/bin/python
print 'Access-Control-Allow-Origin: *'
print 'Content-Type: text/html\n'     # HTML is following
import os
import tempfile
import base64
import cgi
import cgitb
import re
import urllib2
import json
import gd
import pysam
import base64
from random import randint

cgitb.enable()

def generate_colour(start, end, percent):
	# print percent
	start_color = start
	end_color = end

	start_red = int(start[0:2], 16)
	start_green = int(start[2:4], 16)
	start_blue = int(start[4:6], 16)

	#print start_red, start_green, start_blue, "<br/>"

	end_red = int(end[0:2], 16)
	end_green = int(end[2:4], 16)
	end_blue = int(end[4:6], 16)

	#print end_red, end_green, end_blue, "<br/>"

	diff_red = ((end_red - start_red) * percent) + start_red;
	diff_green = ((end_green - start_green) * percent) + start_green;
	diff_blue = ((end_blue - start_blue) * percent) + start_blue;

	#print diff_red, diff_green, diff_blue, "<br/>"

	hex_red = hex(int(diff_red))[2:]
	hex_green = hex(int(diff_green))[2:]
	hex_blue = hex(int(diff_blue))[2:]

	return (diff_red, diff_green, diff_blue)

print generate_colour("FF0000", "FFFF00", 1)

# ----- CONSTANTS -----
EXON_IMG_WIDTH = 100
EXON_IMG_HEIGHT = 10

exongraph = gd.image((EXON_IMG_WIDTH, EXON_IMG_HEIGHT))

# Define the colours
white = exongraph.colorAllocate((255,255,255))
black = exongraph.colorAllocate((0,0,0))

red = exongraph.colorAllocate((220,20,60))
orange = exongraph.colorAllocate((255,140,0))
blue = exongraph.colorAllocate((0,0,255))
# TO DO: Fix the green and dark green shades...
green = exongraph.colorAllocate((166,220,166))
darkgreen = exongraph.colorAllocate((0,125,0))

count = 0 # Need a comma if the it is not the first element...
for iiii in range(EXON_IMG_WIDTH):
	variable_colour = exongraph.colorAllocate(generate_colour("FF0000", "FFFF00", float(iiii*1.0/EXON_IMG_WIDTH)))
	exongraph.filledRectangle((iiii, 0), (iiii, EXON_IMG_HEIGHT), variable_colour)

exongraph.string(0, (0, 1), "Max", black)
exongraph.string(0, (EXON_IMG_WIDTH-5, 1), "0", black)
#exongraph.string(0, (EXON_IMG_WIDTH-15, 1), "Min", black)

f = open("get_exon_base64_exongraph.png", "w")
exongraph.writePng(f)
f.close()

printout = ""

with open("get_exon_base64_exongraph.png", "rb") as fl:
	printout = printout + fl.read().encode("base64")

print('<img src="get_exon_base64_exongraph.png" />')
print "</br>"
print "</br>"
print(printout)

fl.close()