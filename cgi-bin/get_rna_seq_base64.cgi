#!/usr/bin/python
# Displays the XML file in a browser
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


# ----- CONSTANTS -----

RNA_IMG_WIDTH = 450
RNA_IMG_HEIGHT = 50

REGEX = '(/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits\.bam)'

# ----- CLEAR OLD FILES -----
img_files = []
img_files.append("rnaseqgraph0.png")
img_files.append("rnaseqgraph1.png")
img_files.append("rnaseqgraph2.png")
img_files.append("rnaseqgraph3.png")
img_files.append("rnaseqgraph4.png")
img_files.append("rnaseqgraph5.png")
for img_file in img_files:
    f = open(img_file, "w+")
    red_sqr = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))
    red_clr = red_sqr.colorAllocate((255,255,255))
    red_sqr.rectangle((0,0), (RNA_IMG_WIDTH, RNA_IMG_HEIGHT), red_clr)
    red_sqr.writePng(f)
    f.close()


geneid = cgi.FieldStorage().getvalue('locus')


# ----- GETS MAPPING INFO FOR THE GENE ID -----
map_info = json.loads(urllib2.urlopen("http://bar.utoronto.ca/webservices/araport/gff/get_tair10_gff.php?locus=" + geneid).read())

start = map_info[u'result'][0][u'start'] if map_info[u'result'][0][u'strand'] == u'+' else map_info[u'result'][0][u'end']
end = map_info[u'result'][0][u'end'] if map_info[u'result'][0][u'strand'] == u'+' else map_info[u'result'][0][u'start']
chromosome = int(map_info[u'result'][0][u'chromosome'])

'''
Figures out true starts and ends of the CDS based on the information retrieved into map_info.
'''
for region in map_info[u'result']:
	if region[u'strand'] == u'+':
		if region[u'start'] < start:
			start = region[u'start']
		if region[u'end'] > end:
			end = region[u'end']
	else:
		if region[u'start'] < start:
			start = region[u'start']
		if region[u'end'] > end:
			end = region[u'end']

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def generate_rnaseq_graph(urlx, filename, out_clr):
	xvalues = []
	values = []
	#print "<br/>GENERATING RNA SEQ GRAPH! colour = " + str(hex_to_rgb(out_clr))  
	#print "Chr%s :: %s-%s url = %s" %(chromosome, start, end, urlx)
	#print "<br/><br/>urlx = " + "mpileups/"+urlx + "; out = " + filename + "<br/><br/>"
	if urlx == "":
		return
	match = re.search(REGEX, urlx)
	if match:
		filename2 = match.group(2) + "_" + geneid
	try:
		for read in open("mpileups/"+urlx):
			#print("<br/>{0}".format(float(read.split('\t')[1])))
			#print("x = {0}, y = {1}<br/>".format(float(read.split('\t')[1]), float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>'))))
			xvalues.append(float(read.split('\t')[1]))
			values.append(float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>')))
		values = [int(x / max(values) * RNA_IMG_HEIGHT) for x in values]
		rnaseqgraph = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))
		white = rnaseqgraph.colorAllocate((255,255,255))
		green = rnaseqgraph.colorAllocate(hex_to_rgb(out_clr))
		for i in range(len(xvalues)):
			#print("x = {0} ---> reactangle({1}, {2}, {3}, {4})<br/>".format(xvalues[i], int(float(xvalues[i] - start) /(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT, int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]))
			rnaseqgraph.rectangle((int(float(xvalues[i] - start) /(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT), (int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]), green)
		f = open(filename, "w+")
		rnaseqgraph.writePng(f)
		f.close()
	except pysam.SamtoolsError as msg:
		print "<br/><br/>pysam.SamtoolsError was raised for locus = " + geneid + " in experiment = " + match.group(2) + " BAM file. ERR MSG >>>" + str(msg) + "<br/>"



e = xml.etree.ElementTree.parse('data/bamdata_amazon_links.xml')


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
colour = False
bold = False
clr = ""
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
				clr = child.attrib.get(key)[2:]
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
				"name": "<a href='" + child.attrib.get(key) + "'>bam file link </a> <br />", 
				"url": child.attrib.get(key), 
				"img": child.attrib.get(key) + ".png", 
			}
			if key == "svgname":
				print open("SVGs/" + child.attrib.get(key)[4:], "r").read()
			elif key in cases.keys():
				print cases[key]
				if key == "name":
					img_file_name = (cases["img"][66:]).replace("/", "_").replace(".bam", "")
					print "<br/>Read from: " + (cases["img"][66:]).replace("/", "_").replace(".png", "")
					img_file_name = "img/" + img_file_name
					print "<br/>Output went to: " + img_file_name
					generate_rnaseq_graph((cases["img"][66:]).replace("/", "_").replace(".png", ""), img_file_name, clr)
					print '<img src="' + img_file_name + '">'
					print '<br/>'
					print '<img src="exongraph.png">'
			else:
				print child.attrib[key]
			if bold:
				print "</b>"
		print "</td>"
	print "</tr>"

print "</table>"