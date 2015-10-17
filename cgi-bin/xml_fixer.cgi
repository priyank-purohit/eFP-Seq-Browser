#!/usr/bin/python
"""
The for loop searches through links from XML1 and finds correspending URLs from file #2.
This code was implemented in xmlparser.cgi file (or maybe it's under a different name now)
"""
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>XML Fixer</title>"

import xml.etree.ElementTree
import re
import sys
import os
import cgi
import cgitb
cgitb.enable()

original = xml.etree.ElementTree.parse('data/bamlocator.xml').getroot()
new = xml.etree.ElementTree.parse('data/iplant_path_to_rnaseq_bam_files.xml').getroot()

REGEX = '(http://newland\.iplantcollaborative\.org/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits\.bam)'
REGEX_new = '(/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits\.bam[^.bai])'

print "<body>"

for entry in original.findall('file'):
    url = entry.get('name')
    #print(url + "<br/>")
    match = re.search(REGEX, url)
    if (match):
        #print("----" + match.group(2) + "<br/>")
        original_exp = match.group(2)
        original_url = match.group(1)
        for line in open('data/iplant_path_to_rnaseq_bam_files.txt'):
            #print("<br/>" + line)
            match2 = re.search(REGEX_new, line)
            if (match2):
                #print(match2.group(2))
                new_exp = match2.group(2)
                new_url = match2.group(1)
                if (original_exp == new_exp):
                    print(original_exp + " --> " + new_exp + "<br/>")
                    entry.value = "XXX"
    

        

print "</body>"
print "</html>"