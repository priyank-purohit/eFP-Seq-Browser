#!/usr/bin/python

# This script checks whether the number of mapped reads counted by the two different methods gave the same answer.

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
import os
import cgi
import cgitb
cgitb.enable()
import xml.etree.ElementTree
import tempfile
import base64
import re
import urllib2
import json
import gd
import pysam
from random import randint
cgitb.enable()

file1 = "AT1G01010/_read_counts_bam_wc_bedtools.txt";
file2 = "AT2G24270/_read_counts_bam_wc_bedtools.txt";
file3 = "AT3G24650/_read_counts_bam_wc_bedtools.txt";
file4 = "AT3G24660/_read_counts_bam_wc_bedtools.txt";
file5 = "AT5G66460/_read_counts_bam_wc_bedtools.txt";

list_of_files = [];

list_of_files.append(file1);
list_of_files.append(file2);
list_of_files.append(file3);
list_of_files.append(file4);
list_of_files.append(file5);

file_contents = []

for each_file in list_of_files:
	for line in open(each_file):
		file_contents.append(line.strip('\n'))

print "<br/>"
print "<br/>"
print "<br/>"

# Print "Found at least one" if there is a mismatch ..!
for i in range(1, 113*5+1):
	print "Comparing: " + file_contents[(i*3)-2] + " to " + file_contents[(i*3) - 1] + "<br/>"
	if (file_contents[(i*3)-2] != file_contents[(i*3) - 1]):
		print "<br/><br/><br/> ************ FOUND AT LEAST ONE! *************** <br/><br/><br/>"
