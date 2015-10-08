#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>RNA Browser (Priyank)</title>"

import os
import cgi
import cgitb
import re
cgitb.enable()
import urllib2
import json
import gd
import pysam

# ----- CONSTANTS -----
EXON_IMG_WIDTH = 200
EXON_IMG_HEIGHT = 15

RNA_IMG_WIDTH = 200
RNA_IMG_HEIGHT = 200


# ----- LOCUS TAGS OF INTEREST -----
ABI3 = "AT3G24650"
TMKL1 = "AT3G24660"


# ----- LOCUS TAG TO DISPLAY -----
geneid = "AT1G01010"
geneid = "AT4G25960"

print '<style>'
print 'td {text-align:center;}'
print '</style>'


# ----- BAM FILE LINK -----
url = "http://newland.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/ERR274310/accepted_hits.bam"


# ----- GETS MAPPING INFO FOR THE GENEID -----
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
	f = open("exongraph.png", "w")
	exongraph.writePng(f)
	f.close()

def generate_rnaseq_graph():
	xvalues = []
	values = []
	#print "Chr%s :: %s-%s" %(chromosome, start, end)
	for read in pysam.mpileup(url, "-r", "Chr%s:%s-%s" %(chromosome, start, end)): 
		#print("<br/>{0}".format(float(read.split('\t')[1])))
		xvalues.append(float(read.split('\t')[1]))
		values.append(float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>')))
	values = [int(x / max(values) * RNA_IMG_HEIGHT) for x in values]
	rnaseqgraph = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))
	white = rnaseqgraph.colorAllocate((255,255,255))
	green = rnaseqgraph.colorAllocate((0,255,0))
	for i in range(len(xvalues)):
		rnaseqgraph.rectangle((int(float(xvalues[i] - start) /(end-start) * RNA_IMG_WIDTH), RNA_IMG_WIDTH), (int(float(xvalues[i] - start)/(end-start) * RNA_IMG_HEIGHT), RNA_IMG_HEIGHT - values[i]), green)        
	f = open("rnaseqgraph.png", "w")
	rnaseqgraph.writePng(f)
	f.close()




print "<body>"


print "<p>Looking up {0}.</p>".format(geneid)
#print map_info
print "<br/><br/><p>Chromosome = {2}, Start = {0}; End = {1}.</p><br/><br/>".format(start, end, chromosome)

print '<img src="rnaseqgraph.png">'
print '<br/>'
print '<img src="exongraph.png">'

generate_exon_graph()
generate_rnaseq_graph()


print "</body>"
print "</html>"