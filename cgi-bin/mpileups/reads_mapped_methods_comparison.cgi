#!/usr/bin/python

# This script checks whether the number of mapped reads counted by the two 
# methods gave the same answer.

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

import os
import cgi
import cgitb
cgitb.enable()

list_of_files = [];

file1 = "AT1G01010/_read_counts_bam_wc_bedtools.txt";
file2 = "AT2G24270/_read_counts_bam_wc_bedtools.txt";
file3 = "AT3G24650/_read_counts_bam_wc_bedtools.txt";
file4 = "AT3G24660/_read_counts_bam_wc_bedtools.txt";
file5 = "AT5G66460/_read_counts_bam_wc_bedtools.txt";

list_of_files.append(file1);
list_of_files.append(file2);
list_of_files.append(file3);
list_of_files.append(file4);
list_of_files.append(file5);

file_contents = []

for each_file in list_of_files:
	for line in open(each_file): # For each line in each file:
		file_contents.append(line.strip('\n'))

print "<br/>"

# *** Each file content is in the following format ***
# <name of the bam file from which data was generated>
# <mapped reads count produced by the word count method>
# <mapped reads count produced by the bedtools method>

# Print "Found at least one" if there is a mismatch ..!
for i in range(1, 113*5+1):
	print "Comparing: " + file_contents[(i*3)-2] + " to " + file_contents[(i*3) - 1] + "<br/>"
	if (file_contents[(i*3)-2] != file_contents[(i*3) - 1]):
		print "<br/><br/><br/> ************ FOUND AT LEAST ONE! *************** <br/><br/><br/>"
