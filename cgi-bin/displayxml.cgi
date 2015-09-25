#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>bamlocatorxml</title>"

import os
import cgi
import cgitb
cgitb.enable()
import xml.etree.ElementTree

e = xml.etree.ElementTree.parse('data/test.xml')
# note that even though there are some experiments that should be grouped together, they aren't in the xml file, and so the grey white colouring is not useful
print """
<style>
td {padding:0px}
table {border-collapse:collapse}
svg {height:50px;width:auto}
</style>
<table border=1>
"""

current_group = [exp.text for exp in e.getroot()[0].find("groupwith").findall("experiment")]
a = e.getroot()[0].attrib.keys()
a.sort()
colour = False;
for key in a:
	print "<th>" + key + "</th>"

for child in e.getroot():
	if current_group != [exp.text for exp in child.find("groupwith").findall("experiment")]:
		colour = not colour
		current_group = [exp.text for exp in child.find("groupwith").findall("experiment")]
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
			cases = {
				"url": "<a href='" + child.attrib.get(key) + "'>URL link </a> <br />",
				"publicationid": "<a href='" + child.attrib.get(key) + "'> publication link </a> <br />",
				"name": "<a href='" + child.attrib.get(key) + "'>bam file link </a> <br />", 
			}
			if key == "subunitname":
				print open("SVGs/" + child.attrib.get(key)[4:], "r").read()
			elif key in cases.keys():
				print cases[key]
			else:
				print child.attrib[key]
		print "</td>"
	print "</tr>"

print "</table>"