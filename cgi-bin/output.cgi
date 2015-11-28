#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>RNA Browser (PKP)</title>"

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

# ----- CONSTANTS -----
EXON_IMG_WIDTH = 450
EXON_IMG_HEIGHT = 7

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

# ----- LOCUS TAGS OF INTEREST -----
ABI3 = "AT3G24650"
TMKL1 = "AT3G24660"
GAPDH = "AT2G24270"


# ----- LOCUS TAG TO DISPLAY -----
geneidx = "AT1G01010"
geneidx = "AT5G66460"
geneidx = TMKL1
geneid = cgi.FieldStorage().getvalue('locus')


print '<style>'
print 'td {text-align:center;}'
print '</style>'


# ----- BAM FILE LINK -----
url0 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/ERR274310/accepted_hits.bam"
url1 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/SRR547531/accepted_hits.bam"
url11 = "http://bar.utoronto.ca/~ppurohit/RNA-Browser/cgi-bin/data/iplant/home/araport/rnaseq_bam/aerial/SRR547531/accepted_hits.bam"
url11 = "data/iplant/home/araport/rnaseq_bam/aerial/SRR547531/accepted_hits.bam"
url2 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/SRR548277/accepted_hits.bam"
url3 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/SRR847503/accepted_hits.bam"
url4 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/SRR847504/accepted_hits.bam"
url5 = "http://vision.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/SRR847505/accepted_hits.bam"


# Not being used right now but can use it...
url_arr = []
url_arr.append(url0)
url_arr.append(url1)
url_arr.append(url2)
url_arr.append(url3)
url_arr.append(url4)
url_arr.append(url5)


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






'''
Generates exon-intron image based on the information in map_info.
'''
def generate_exon_graph():
	exongraph = gd.image((EXON_IMG_WIDTH, EXON_IMG_HEIGHT))
	white = exongraph.colorAllocate((255,255,255))
	black = exongraph.colorAllocate((0,0,0))
	blue = exongraph.colorAllocate((0,0,255))
	exongraph.lines(((0, EXON_IMG_HEIGHT), (EXON_IMG_WIDTH, EXON_IMG_HEIGHT)), black)
	for region in map_info[u'result']:
		if region[u'type'] == u'exon':
			#print (float(region[u'start'] - start) /(end-start), float(region[u'end'] - start)/(end-start))
			exongraph.filledRectangle((int(float(region[u'start'] - start) /(end-start) * EXON_IMG_WIDTH), EXON_IMG_HEIGHT), (int(float(region[u'end'] - start)/(end-start) * EXON_IMG_WIDTH), 0), blue)
	
	exongraph.filledRectangle((0, 3), (EXON_IMG_WIDTH, 3), blue)
	f = open("exongraph.png", "w")
	exongraph.writePng(f)
	f.close()
	with open("exongraph.png", "rb") as fl:
		print "base64 = {0}.".format(fl.read().encode("base64"))
	fl.close()



def generate_rnaseq_graph(urlx, filename):
	xvalues = []
	values = []
	#print "<br/>GENERATING RNA SEQ GRAPH!"
	#print "Chr%s :: %s-%s url = %s" %(chromosome, start, end, urlx)
	match = re.search(REGEX, urlx)
	if match:
		filename2 = match.group(2) + "_" + geneid
	try:
		pileup = pysam.mpileup(urlx, "-r", "Chr%s:%s-%s" %(chromosome, start, end))
		for read in pileup:
			#print("<br/>{0}".format(float(read.split('\t')[1])))
			#print("x = {0}, y = {1}<br/>".format(float(read.split('\t')[1]), float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>'))))
			xvalues.append(float(read.split('\t')[1]))
			values.append(float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>')))
		values = [int(x / max(values) * RNA_IMG_HEIGHT) for x in values]
		rnaseqgraph = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))
		white = rnaseqgraph.colorAllocate((255,255,255))
		green = rnaseqgraph.colorAllocate((0,255,0))
		for i in range(len(xvalues)):
			#print("x = {0} ---> reactangle({1}, {2}, {3}, {4})<br/>".format(xvalues[i], int(float(xvalues[i] - start) /(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT, int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]))
			rnaseqgraph.rectangle((int(float(xvalues[i] - start) /(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT), (int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]), green)
		f = open(filename, "w+")
		rnaseqgraph.writePng(f)
		f.close()
	except pysam.SamtoolsError as msg:
		print "<br/><br/>pysam.SamtoolsError was raised for locus = " + geneid + " in experiment = " + match.group(2) + " BAM file. ERR MSG >>>" + str(msg) + "<br/>"

print "<body>"


print "<p>Locus == {0}, Chromosome = {3}, Start = {1}; End = {2}.</p>".format(geneid, start, end, chromosome)
#print map_info

print '<img src="rnaseqgraph0.png">'
print '<br/>'
print '<img src="exongraph.png">'
"""
print '<br/>'
print '<img src="rnaseqgraph1.png">'
print '<br/>'
print '<img src="exongraph.png">'

print '<br/>'
print '<img src="rnaseqgraph2.png">'
print '<br/>'
print '<img src="exongraph.png">'

print '<br/>'
print '<img src="rnaseqgraph3.png">'
print '<br/>'
print '<img src="exongraph.png">'

print '<br/>'
print '<img src="rnaseqgraph4.png">'
print '<br/>'
print '<img src="exongraph.png">'

print '<br/>'
print '<img src="rnaseqgraph5.png">'
print '<br/>'
print '<img src="exongraph.png">'
"""

generate_exon_graph()

generate_rnaseq_graph(url11, "rnaseqgraph0.png")
#generate_rnaseq_graph(url1, "rnaseqgraph1.png")
#generate_rnaseq_graph(url2, "rnaseqgraph2.png")
#generate_rnaseq_graph(url3, "rnaseqgraph3.png")
#generate_rnaseq_graph(url4, "rnaseqgraph4.png")
#generate_rnaseq_graph(url5, "rnaseqgraph5.png")

print "</body>"
print "</html>"