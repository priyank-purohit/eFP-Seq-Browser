#!/usr/bin/python
# Displays the XML file in a browser
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<!DOCTYPE html>"
print "<html>"
print "<head>"
print "	<title>BAM Locator XML</title>"
# note that even though there are some experiments that should be grouped together, they aren't in the xml file, and so the grey white colouring is not useful
print """
	<style>
	td {padding:0px}
	table {border-collapse:collapse}
	svg {height:50px;width:auto}
	</style>
</head>
"""

import os
import cgi
import cgitb
import xml.etree.ElementTree
cgitb.enable()

e = xml.etree.ElementTree.parse('data/bamdata_amazon_links.xml')

print """
<body>
	<table style=\"border: 1px solid grey;\">
"""
experiments_arr = [exp.text for exp in e.getroot()[0].find("groupwith").findall("experiment")]
file_attr_keys = e.getroot()[0].attrib.keys()
file_attr_keys.sort()

colour = False
bold = False
for key in file_attr_keys:
	print "<th style=\"border: 1px solid grey; font-size: 14pt;\">" + key + "</th>"

for child in e.getroot():
	if experiments_arr != [exp.text for exp in child.find("groupwith").findall("experiment")]:
		colour = not colour
		experiments_arr = [exp.text for exp in child.find("groupwith").findall("experiment")]
	if child.attrib.get('experimentno') in [exp.text for exp in child.find("control").findall("experiment")]:
		#bold this line
		bold = True
	else:
		bold = False
	keys = child.attrib.keys()
	keys.sort()

	#alternate colouring
	if colour:
		print "<tr style=\"background-color: #D3D3D3; border: 1px solid grey;\">"
	else:
		print "<tr style=\"background-color: #FFFFFF; border: 1px solid grey;\">"

	for key in file_attr_keys:
		if key == "foreground":
			try:
				print "<td style=\"background-color:#" + child.attrib.get(key)[2:] + "; border: 1px solid grey;\">"
			except:
				print "<td style=\"border: 3px solid red;\">"
		else: 
			print "<td style=\"border: 1px solid grey;\">"

		if child.attrib.get(key):
			if bold:
				print "<b>"
			cases = {
				"url": "<a href='" + child.attrib.get(key) + "'>URL Link</a><br />",
				"publicationid": "<a href='" + child.attrib.get(key) + "'> Publication Link</a><br />",
				"name": "<a href='" + child.attrib.get(key) + "'>BAM File Link</a><br />", 
			}
			if key == "svgname":
				print open("SVGs/" + child.attrib.get(key)[4:], "r").read()
			elif key in cases.keys():
				print cases[key]
			else:
				print child.attrib[key]

			if bold:
				print "</b>"
		print "</td>"
	print "</tr>"

print """
</table>
</body>
</html>"""