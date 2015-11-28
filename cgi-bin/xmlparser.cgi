#!/usr/bin/python
# Just displays the new links w/o editing the XML file
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print                               # blank line, end of headers
print "<title>NEW Bar Locator (PKP)</title>"

import xml.etree.ElementTree
import re
import sys
import os
import cgi
import cgitb
cgitb.enable()

e = xml.etree.ElementTree.parse('data/bamdata_rsong_vision_links.xml')
original = xml.etree.ElementTree.parse('data/bamdata_rsong_vision_links.xml').getroot()
#new = xml.etree.ElementTree.parse('data/iplant_path_to_rnaseq_bam_files.xml').getroot()
REGEX = '(http://newland\.iplantcollaborative\.org/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits\.bam)'
REGEX_new = '(/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits\.bam[^.bai])'
print """
<style>
td {padding:0px}
table {border-collapse:collapse}
svg {height:50px;width:auto}
</style>
<table border=1>
"""
def get_new_link_old(ori_exp):
	ret = "9889"
	print "XX: LOOKING FOR " + ori_exp
	for entry in original.findall('file'):
		url = entry.get('name')
		#print(url + "<br/>")
		match = re.search(REGEX, url)
		if match:
		    original_exp = match.group(2)
		    original_url = match.group(1)
		    if original_exp == ori_exp:
		    	print("XX: " + original_exp + "<br/>")
		    	for line in open('data/iplant_path_to_rnaseq_bam_files.txt'):
			        #print("<br/>" + line)
			        match2 = re.search(REGEX_new, line)
			        if match2:
			            new_exp = match2.group(2)
			            new_url = match2.group(1)
			            if original_exp == new_exp:
			            	ret = "http://vision.iplantcollaborative.org" + match2.group().rstrip('\n')
	return ret

def get_new_link(ori_exp):
	ret = "NO NEW LINKS FOUND!"
	for line in open('data/iplant_path_to_rnaseq_bam_files.txt'):
		match = re.search(REGEX_new, line)
		if match:
			new_exp = match.group(2)
			new_url = match.group(1)
			if ori_exp == new_exp:
				ret = "http://vision.iplantcollaborative.org" + match.group().rstrip('\n')
	return ret

current_group = [exp.text for exp in e.getroot()[0].find("groupwith").findall("experiment")]
a = e.getroot()[0].attrib.keys()
a.sort()
colour = False
bold = False
for key in a:
	print "<th>" + key + "</th>"

for child in e.getroot():
	if current_group != [exp.text for exp in child.find("groupwith").findall("experiment")]:
		colour = not colour
		current_group = [exp.text for exp in child.find("groupwith").findall("experiment")]
	if child.attrib.get('experimentno') in [exp.text for exp in child.find("control").findall("experiment")]:
		#bold this line
		bold = True
	else:
		bold = False
	keys = child.attrib.keys()
	keys.sort()
	#alternate colouring
	print "<tr style=\""
	if colour:
		print "background-color:#d3d3d3"
	else:
		print "background-color:white"
	print "\">"
	for key in a:
		if key == "foreground":
			try:
				print "<td style=\"background-color:#" + child.attrib.get(key)[2:] + "\">"
			except:
				print "<td>"
		else: 
			print "<td>" 
		if child.attrib.get(key):
			if bold:
				print "<b>"
			cases = {
				"url": "<a href='" + child.attrib.get(key) + "'>URL link </a> <br />",
				"publicationid": "<a href='" + child.attrib.get(key) + "'> publication link </a> <br />",
				"name": "<a href='" + child.attrib.get(key) + "'>OLD BAM </a> <br /><br />", 
			}
			if key == "subunitname":
				print open("SVGs/" + child.attrib.get(key)[4:], "r").read()
			elif key in cases.keys():
				if (key == "name"):
					match = re.search(REGEX, cases[key])
					if match:
						print (get_new_link(str(match.group(2)))+"<br />")
				else:
					print cases[key]
			else:
				print child.attrib[key]
			if bold:
				print "</b>"
		print "</td>"
	print "</tr>"

print "</table>"