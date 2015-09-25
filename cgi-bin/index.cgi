#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>hello world</title>"

import os
import cgi
import cgitb
import re
cgitb.enable()
import urllib2
import json
import gd
import pysam

geneid = "At1g11190"
print "Looking up %s" %geneid
j = json.loads(urllib2.urlopen("http://bar.utoronto.ca/webservices/araport/gff/get_tair10_gff.php?locus=" + geneid).read())
start = j[u'result'][0][u'start'] if j[u'result'][0][u'strand'] == u'+' else j[u'result'][0][u'end']
end = j[u'result'][0][u'end'] if j[u'result'][0][u'strand'] == u'+' else j[u'result'][0][u'start']
chromosome = int(j[u'result'][0][u'chromosome'])
for region in j[u'result']:
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

def generate_exon_graph():
	exongraph = gd.image((200, 100))
	white = exongraph.colorAllocate((255,255,255))
	black = exongraph.colorAllocate((0,0,0))
	red = exongraph.colorAllocate((255,0,0))
	exongraph.lines(((0, 50), (200, 50)), black)
	for region in j[u'result']:
		if region[u'type'] == u'exon':
			print (float(region[u'start'] - start) /(end-start), float(region[u'end'] - start)/(end-start))
			exongraph.filledRectangle((int(float(region[u'start'] - start) /(end-start) * 200), 65), (int(float(region[u'end'] - start)/(end-start) * 200), 35), red)        

	print f

def generate_rnaseq_graph():
	url = "http://newland.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/ERR274310/accepted_hits.bam"
	xvalues = []
	values = []
	print "Chr%s:%s-%s" %(chromosome, start, end)
	for read in pysam.mpileup(url, "-r", "Chr%s:%s-%s" %(chromosome, start, end)): 
		xvalues.append(float(read.split('\t')[1]))
		values.append(float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>')))

	values = [int(x / max(values) * 200) for x in values]

	rnaseqgraph = gd.image((200, 200))
	white = rnaseqgraph.colorAllocate((255,255,255))
	black = rnaseqgraph.colorAllocate((0,0,0))
	for i in range(len(xvalues)):
		rnaseqgraph.rectangle((int(float(xvalues[i] - start) /(end-start) * 200), 200), (int(float(xvalues[i] - start)/(end-start) * 200), 200 - values[i]), black)        

	f = open("rnaseqgraph.png", "w")
	rnaseqgraph.writePng(f)
	f.close()





svg = open("SVGs/youngSeedling.svg", "r")
data = svg.read()

form = cgi.FieldStorage()
print '<script src="//code.jquery.com/jquery-1.11.3.min.js"> </script>'
javascript = (
	"""
	$(document).ready(function () {
		$("#go").val('Stop');
	});
	"""
)
print '<script src="sort.js"> </script>'
print '<script >%s</script>' % javascript
print '<style>'
print 'td {text-align:center;}'
print '</style>'
print "<body>"
print '<input id="name" />'
print '<input type="button" id="go" type="button" name="Go" value="Go"/>'
print '	<table border="1" class="sortable" style="width:100%" align="centre">' #set cellpadding to 0.
print '			<th> Expt </th>'
print '			<th> RNA-Seq Coverage <br /><img src="test.png"> </th>'
print '			<th> eFP - RPKM </th>'
print '			<th> SRA Record </th>'
print '			<th> Details </th>'

files = [ f for f in os.listdir("SVGs") if os.path.isfile(os.path.join("SVGs",f)) ]
for item in files:
	svg = open("SVGs/" + item, "r")
	data = svg.read()
	print '		<tr>'
	print '			<td> WT </td>'
	print '			<td> <img src="rnaseqgraph.png"> </td>'
	print '			<td>' + data.replace('fill="none"', 'fill="blue"') + '</td>'
	print '			<td> <a> SRA12345 </a> </td>'
	print '			<td> <a> See Filichkin et. al 2010 </a> </td>'
	print '		</tr>'
print '	</table>'

print form.getvalue("name")
generate_exon_graph()
generate_rnaseq_graph()
print "</body>"
# print "</html>"