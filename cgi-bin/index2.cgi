#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>RNA seq data</title>"

import sys
import cgi
import cgitb
import xml.etree.ElementTree as ET
import svgwrite
import urllib2
import json
import pysam

cgitb.enable()
form = cgi.FieldStorage()

geneid = "At1g11190"
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
			
def generate_rnaseq_graph():
	url = "http://newland.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/aerial/ERR274310/accepted_hits.bam"
	xvalues = []
	values = []
	print "Chr%s:%s-%s" %(chromosome, start, end)
	print (pysam.mpileup(url, "-r", "Chr%s:%s-%s" %(chromosome, start, end)) if pysam.mpileup(url, "-r", "Chr%s:%s-%s" %(chromosome, start, end)) else "wasn't found") #This takes too long!
	# i think the function is returning after a timeout because of how the server works... it's not a malformed call =( we may have to refactor this into another process, and load using ajax?
	for read in pysam.mpileup(url, "-r", "Chr%s:%s-%s" %(chromosome, start, end)): 
		print "got here"
		xvalues.append(float(read.split('\t')[1]))
		values.append(float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>')))

	values = [int(x / max(values) * 200) for x in values]
	
	dwg = svgwrite.Drawing()
	print xvalues
	print values
	for i in range(len(xvalues)):
		dwg.add(dwg.rect(insert=(int(float(xvalues[i] - start) /(end-start) * 200), 200 - values[i]), size=(1, values[i])))
	print dwg.tostring()

experiment = form.getvalue("exp")
tree = ET.parse('./data/bamlocator.xml')
root = tree.getroot()
xmlentry = None
for file in root:
	if file.get("experimentno") == experiment:
		xmlentry = file
if xmlentry is None:
	print experiment + " could not be found"
	sys.exit(0)

html = """
<style>
td {padding: 0px}
table {
	margin: 0 auto;
	width: 75%;
	padding: 0px;
	text-align: center;
}
</style>
<body>
	<table border="1" class="sortable">
		<th> Expt </th>
		<th> RNA-Seq Coverage <br /></th>
		<th> eFP - RPKM </th>
		<th> SRA Record </th>
		<th> Details </th>

"""
group_members_experimentno = []
for group_member in xmlentry.findall(".//experiment"):
	group_members_experimentno.append(group_member.text)
for file in root:
	if file.get("experimentno") in group_members_experimentno:
		html += """
		<tr>
			<td>""" + file.get("experimentno") + """ </td>
			<td>""" + "the graph goes here." + """ </td>
			<td>""" + "eFP goes here." + """ </td>
			<td> <a href='""" + file.get("url") + """'> this entry's SRA record </a> </td>
			<td>""" + file.get("description") + """ </td>
		<tr>
		"""
		group_members_experimentno.remove(file.get("experimentno"))
if len(group_members_experimentno) != 0:
	for no_data_item in group_members_experimentno:
		html += """
		<tr>
			<td>""" + no_data_item + """ </td>
			<td>""" + "no data" + """ </td>
			<td>""" + "no data" + """ </td>
			<td> <a href='""" + """'> no data </a> </td>
			<td>""" + "no data" + """ </td>
		<tr>
		"""

html += """
	</table>
	<br>
	<br>
	<br>
	<br>
	<br>
	<br>
	
"""
dwg = svgwrite.Drawing(profile='tiny')
dwg.add(dwg.line(start=(0, 0), end=(300, 100), stroke=svgwrite.rgb(10, 10, 50, '%')))
dwg.add(dwg.text('Test', insert=(50, 10), fill='red'))
html += dwg.tostring()
html += """
</body>
"""

print html