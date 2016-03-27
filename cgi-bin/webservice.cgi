#!/usr/bin/python
print "Access-Control-Allow-Origin: *"
################################################################################
# This program return the base64 of the image given an AGI, record and tissue
# Authors: Asher and Priyank
# Date: January 2016
# usage:
################################################################################

import base64
import cgi
import cgitb
import re
import json
import sys
import base64
import gd
import random
import urllib2
import os
import subprocess

cgitb.enable()

################################################################################
# Validate data

# Validate Tissue format
def validateTissue(tissue):
	''' Check the format of tissue string and returns error if incorrect. '''

	if tissue == "":
		error("No tissue specified.")
	elif re.search(r'^[a-zA-Z]{1,15}$', tissue): # Can only have upto 15 alpha numeric charactors
		return tissue
	else:
		error("Tissue specifed is not in correct format.");

# Validate locus format
def validateLocus(locus):
	''' Check the format of locus '''

	if locus == "":
		error("No locus specified.")
	elif re.search(r'^at[12345cm]g\d+$', locus, re.I):
		return locus
	else:
		error("Locus format is not correct.")

# Validate record
def validateRecord(record):
	''' Check for format of record '''

	if record == "":
		error("No record specified.")
	elif re.search(r'^\D{3}\d{1,10}$', record):
		return record
	else:
		error("Record format is not correct.")

# Validate Chromosome
def validateChromosome(chromosome):
	# TODO
	return chromosome
	
# Validate Start
def validateStart(start):
	# TODO
	return start

# Validate Stop
def validateStop(stop):
	# TODO
	return stop

################################################################################
# Data processing functions

# Get cooridinates from BAR webservice
def getCoordinatesAndValidateVariants(locus, q_variant):
	''' Get coordinates from webservice '''
	data = json.loads(urllib2.urlopen("http://bar.utoronto.ca/~ppurohit/RNA-Browser/cgi-bin/get_gene_structures.cgi?locus=" + locus).read().replace('\n', ' '))
	#data = json.loads('{"locus" : "AT2G24270", "splice_variants" : [{"exon_coordinates" : [{"exon_start" : 10326918, "exon_end" : 10327438}, {"exon_start" : 10327519, "exon_end" : 10327635}, {"exon_start" : 10327716, "exon_end" : 10328094}, {"exon_start" : 10328181, "exon_end" : 10328336}, {"exon_start" : 10328414, "exon_end" : 10328550}, {"exon_start" : 10328624, "exon_end" : 10328743}, {"exon_start" : 10328836, "exon_end" : 10328964}, {"exon_start" : 10329058, "exon_end" : 10329251}, {"exon_start" : 10329457, "exon_end" : 10330048}], "start" : 10326918, "end" : 10330048, "gene_structure" : "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAHAgMAAADmJKVlAAAACVBMVEX///8AAAAAAP9TU0bQAAAA OElEQVQokWNYhQFWMDBwgWgoBQcLGBi0VkEkmKDqtCAUjMsEVckAAVqYZoNMGZk20hYMDj8OOxsB 8HKcqJcHFfUAAAAASUVORK5CYII= "}, {"exon_coordinates" : [{"exon_start" : 10326925, "exon_end" : 10327438}, {"exon_start" : 10329457, "exon_end" : 10329618}, {"exon_start" : 10329722, "exon_end" : 10330008}], "start" : 10326925, "end" : 10330008, "gene_structure" : "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAHAgMAAADmJKVlAAAACVBMVEX///8AAAAAAP9TU0bQAAAA JUlEQVQokWNYhQFWMFALaIHNWwBkIUxfwDAybaQtGBx+HHY2AgC1NNrpP7P0gwAAAABJRU5ErkJg gg== "}, {"exon_coordinates" : [{"exon_start" : 10327035, "exon_end" : 10327438}, {"exon_start" : 10329457, "exon_end" : 10329607}, {"exon_start" : 10329722, "exon_end" : 10329941}], "start" : 10327035, "end" : 10329941, "gene_structure" : "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAHAgMAAADmJKVlAAAACVBMVEX///8AAAAAAP9TU0bQAAAA IklEQVQokWNYhQpWMFATMCHMhFmwgGEE2khzMAj8OBxtBAAddMY9TQm56QAAAABJRU5ErkJggg== "}, {"exon_coordinates" : [{"exon_start" : 10327035, "exon_end" : 10327134}, {"exon_start" : 10327330, "exon_end" : 10327438}], "start" : 10327035, "end" : 10329618, "gene_structure" : "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAHAgMAAADmJKVlAAAACVBMVEX///8AAAAAAP9TU0bQAAAA IklEQVQokWNYBQQLGCCACcRZwUBjMFJspCdYMGJCla42AgAJ+HKdI6JOmQAAAABJRU5ErkJggg== "}], "variant_count" : "4"}')

	variant_count = 0
	for variant in data[u'splice_variants']:
		variant_count = variant_count + 1

	if int(q_variant) > int(variant_count):
		error("Bad query :: " + str(q_variant) + "<=" + str(variant_count))

	# This is for using variants' start/end
	'''
	variant_count = 0
	for variant in data[u'splice_variants']:
		variant_count = variant_count + 1
		if (int(q_variant) == int(variant_count)):
			start = int(data[u'splice_variants'][int(q_variant)-1][u'start'])
			end = int(data[u'splice_variants'][int(q_variant)-1][u'end'])
	'''

	chromosome = int(locus[2])
	start = int(data[u'locus_start'])
	end = int(data[u'locus_end'])

	return chromosome, start, end

# For converting from HEX to RGB values
# http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
def hex_to_rgb(val):
    val = val.lstrip('0x')
    length = len(val)
    return tuple(int(val[i:i + length // 3], 16) for i in range(0, length, length // 3))


# Make Image
def makeImage(filename, chromosome, start, end, record, yscale):
	''' Once we have chromosome, start, end and filename, we can make the image.'''

	EXON_IMG_WIDTH = 450
	EXON_IMG_HEIGHT = 7

	RNA_IMG_WIDTH = 450
	RNA_IMG_HEIGHT = 50

	highest_mapped_reads_count = 0 # For setting the appropriate Y scale

	xvalues = [] # Holds nucleotide positions...
	values = [] # Holds the valid mapped reads for the position...

	# Clear temporary files and name a new one
	os.system("find ../temp/* -mtime +1 -exec rm -f {} \\;")
	tempfile = "../temp/RNASeqGraph_" + str(random.randint(1,1000000)) + ".png"

	# Call samtools and get mpileup
	chromosome = "Chr" + str(chromosome)
	region = chromosome + ":" + str(start) + "-" + str(end)
	mpileup = subprocess.check_output(['samtools', 'mpileup', '-r', region, filename])


	# Read pileup output
	for read in mpileup.splitlines():
		xvalues.append(float(read.split('\t')[1])) # nucleotide position
		# get the number of mapped reads and subtract the reference skips
		mapped_reads_count = float(int(read.split('\t')[3]) - read.split('\t')[4].count('<') - read.split('\t')[4].count('>'))
		values.append(mapped_reads_count)
		# Figure out the max number of reads mapped at any given locus
		if (mapped_reads_count > highest_mapped_reads_count):
			highest_mapped_reads_count = mapped_reads_count

	# IF the user specified a custom y-scale, use that
	if (yscale == -1): # If the user did not specify a yscale, use the highest mapped read count
		yscale = highest_mapped_reads_count
		highest_mapped_reads_count = highest_mapped_reads_count * 1.1 # To leave a little room at top of graph for Y-axis scale label...
	else:
		highest_mapped_reads_count = yscale * 1.1

	# Scale all y-axis values
	for i in range(len(values)):
		values[i] = int(values[i] / highest_mapped_reads_count * RNA_IMG_HEIGHT)


	# Create an image
	rnaseqgraph = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))

	white = rnaseqgraph.colorAllocate((255,255,255))
	red = rnaseqgraph.colorAllocate((255,0,0))
	green = rnaseqgraph.colorAllocate((100,204,101))
	yellow = rnaseqgraph.colorAllocate((255,255,0))
	black = rnaseqgraph.colorAllocate((0,0,0))
	gray = rnaseqgraph.colorAllocate((192,192,192))
	rnaseqgraph.filledRectangle((0, 5), (RNA_IMG_WIDTH, 5), gray) # max line at top

	colours_dict = {'ERR274310' : '0x64cc65', 'SRR547531' : '0x64cc65', 'SRR548277' : '0x64cc65', 'SRR847503' : '0x64cc65', 'SRR847504' : '0x64cc65', 'SRR847505' : '0x64cc65', 'SRR847506' : '0x64cc65', 'SRR1207194' : '0xFFFF00', 'SRR1207195' : '0xFFFF00', 'SRR1019436' : '0xCCCC97', 'SRR1019437' : '0xCCCC97', 'SRR1049784' : '0x989800', 'SRR477075' : '0xCCCC97', 'SRR477076' : '0xCCCC97', 'SRR493237' : '0xCCCC97', 'SRR493238' : '0xCCCC97', 'SRR314815' : '0xFFFF65', 'SRR800753' : '0xFFFF65', 'SRR800754' : '0xFFFF65', 'SRR1105822' : '0x64CC65', 'SRR1105823' : '0x64CC65', 'SRR1159821' : '0x64CC65', 'SRR1159827' : '0x64CC65', 'SRR1159837' : '0x64CC65', 'SRR314813' : '0x64CC65', 'SRR446027' : '0x64CC65', 'SRR446028' : '0x64CC65', 'SRR446033' : '0x64CC65', 'SRR446034' : '0x64CC65', 'SRR446039' : '0x64CC65', 'SRR446040' : '0x64CC65', 'SRR446484' : '0x64CC65', 'SRR446485' : '0x999999', 'SRR446486' : '0x64CC65', 'SRR446487' : '0x999999', 'SRR493036' : '0x64CC65', 'SRR493097' : '0x64CC65', 'SRR493098' : '0x64CC65', 'SRR493101' : '0x64CC65', 'SRR764885' : '0x64CC65', 'SRR924656' : '0x64CC65', 'SRR934391' : '0x64CC65', 'SRR942022' : '0x64CC65', 'SRR070570' : '0xCCCC97', 'SRR070571' : '0xCCCC97', 'SRR1001909' : '0x98FF00', 'SRR1001910' : '0x98FF00', 'SRR1019221' : '0x98FF00', 'SRR345561' : '0x98FF00', 'SRR345562' : '0x98FF00', 'SRR346552' : '0x98FF00', 'SRR346553' : '0x98FF00', 'SRR394082' : '0x98FF00', 'SRR504179' : '0x98FF00', 'SRR504180' : '0x98FF00', 'SRR504181' : '0x98FF00', 'SRR515073' : '0x98FF00', 'SRR515074' : '0x98FF00', 'SRR527164' : '0x98FF00', 'SRR527165' : '0x98FF00', 'SRR584115' : '0x98FF00', 'SRR584121' : '0x98FF00', 'SRR584129' : '0x98FF00', 'SRR584134' : '0x98FF00', 'SRR653555' : '0x98FF00', 'SRR653556' : '0x98FF00', 'SRR653557' : '0x98FF00', 'SRR653561' : '0x98FF00', 'SRR653562' : '0x98FF00', 'SRR653563' : '0x98FF00', 'SRR653564' : '0x98FF00', 'SRR653565' : '0x98FF00', 'SRR653566' : '0x98FF00', 'SRR653567' : '0x98FF00', 'SRR653568' : '0x98FF00', 'SRR653569' : '0x98FF00', 'SRR653570' : '0x98FF00', 'SRR653571' : '0x98FF00', 'SRR653572' : '0x98FF00', 'SRR653573' : '0x98FF00', 'SRR653574' : '0x98FF00', 'SRP018266' : '0x98FF00', 'SRR653576' : '0x98FF00', 'SRR653577' : '0x98FF00', 'SRR653578' : '0x98FF00', 'SRR797194' : '0x98FF00', 'SRR797230' : '0x98FF00', 'SRR833246' : '0x98FF00', 'SRR847501' : '0xFF0000', 'SRR847502' : '0xFF0000', 'SRR1260032' : '0xBD7740', 'SRR1260033' : '0xBD7740', 'SRR1261509' : '0xBD7740', 'SRR401413' : '0xCCFF00', 'SRR401414' : '0xCCFF00', 'SRR401415' : '0xCCFF00', 'SRR401416' : '0xCCFF00', 'SRR401417' : '0xCCFF00', 'SRR401418' : '0xCCFF00', 'SRR401419' : '0xCCFF00', 'SRR401420' : '0xCCFF00', 'SRR401421' : '0xCCFF00', 'ERR274309' : '0xCCCC97', 'SRR1046909' : '0xCCCC97', 'SRR1046910' : '0xCCCC97', 'SRR1524935' : '0xCCCC97', 'SRR1524938' : '0xCCCC97', 'SRR1524940' : '0xCCCC97', 'SRR314814' : '0xCCCC97', 'SRR949956' : '0x999999', 'SRR949965' : '0x999999', 'SRR949988' : '0x999999', 'SRR949989' : '0x999999'}
	
	colour = rnaseqgraph.colorAllocate(hex_to_rgb(colours_dict[record]))

	# Actual RNA-Seq image
	for i in range(len(xvalues)):
		rnaseqgraph.rectangle((int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT), (int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]), colour)
	rnaseqgraph.string(0, (420, 5), str(int(yscale)), black) # y axis scale label

	# Output the GD image to temp PNG file
	f = open(tempfile, "w+")
	rnaseqgraph.writePng(f)
	f.close()

	# Convert the PNG to base64
	with open(tempfile, "rb") as fl:
		base64 = format(fl.read().encode("base64"))

	return base64

################################################################################
# Ouput functions
		
# Error function
def error(string):
	print json.dumps({"status":"failed", "result":string})
	sys.exit(0)

# Final output, if everything at this point succeded
def dumpJSON(status, locus, variant, chromosome, start, end, record, tissue, base64img, reads_mapped_to_locus, abs_fpkm): # and svg_info that will be implemented later on
	print "Content-type: application/json\n"
	print json.dumps({"status": 200, "locus": locus, "variant": variant, "chromosome": chromosome, "start": start, "end": end, "record": record, "tissue": tissue, "rnaseqbase64": base64img, "reads_mapped_to_locus": reads_mapped_to_locus, "absolute-fpkm": abs_fpkm}) # and svg stuff
	sys.exit(0)

################################################################################
# The main program
def main():
	''' This is the main function that gets called when the program start '''
	#print "Content-Type: text/html\n\n"
	
	# Get query details
	form = cgi.FieldStorage()
	tissue = form.getvalue('tissue')
	locus = form.getvalue('locus')
	record = form.getvalue('record')
	variant = form.getvalue('variant')

	if (form.getvalue('yscale')):
		yscale = int(form.getvalue('yscale'))
	else:
		yscale = -1

	chromosome = int(locus[2])
	start = int(form.getvalue('start'))
	end = int(form.getvalue('end'))

	# Now validate the data
	tissue = validateTissue(tissue)
	locus = validateLocus(locus)
	record = validateRecord(record)

	# Now Get the chromosome, start and end from BAR webservice
	#chromosome, start, end = getCoordinatesAndValidateVariants(locus, variant)
	
	region = "Chr" + str(chromosome) + ":" + str(start) + "-" + str(end)

	#'''
	# Make S3FS filename here
	bam_file = "/mnt/RNASeqData/" + tissue + "/" + record + "/accepted_hits.bam"

	# Now make a image using samtools
	base64img = makeImage(bam_file, chromosome, start, end, record, yscale)

	# Count the number of mapped reads to the locus
	lines = subprocess.check_output(['samtools', 'view', bam_file, region])
	mapped_reads = lines.count('Chr')

	reads_in_exp_dict = {'ERR274310' : '29098868', 'SRR547531' : '13627154', 'SRR548277' : '10647001', 'SRR847503' : '19012222', 'SRR847504' : '17652623', 'SRR847505' : '14547829', 'SRR847506' : '14547829', 'SRR1207194' : '41295666', 'SRR1207195' : '39074103', 'SRR1019436' : '22144930', 'SRR1019437' : '24158853', 'SRR1049784' : '51665293', 'SRR477075' : '33569708', 'SRR477076' : '20201654', 'SRR493237' : '27039911', 'SRR493238' : '25704434', 'SRR314815' : '25509908', 'SRR800753' : '7506384', 'SRR800754' : '7063908', 'SRR1105822' : '38483470', 'SRR1105823' : '30583559', 'SRR1159821' : '19343538', 'SRR1159827' : '9138919', 'SRR1159837' : '5659168', 'SRR314813' : '26044624', 'SRR446027' : '31481295', 'SRR446028' : '42228711', 'SRR446033' : '61481964', 'SRR446034' : '63386459', 'SRR446039' : '60325368', 'SRR446040' : '74683660', 'SRR446484' : '30583559', 'SRR446485' : '35231736', 'SRR446486' : '31078655', 'SRR446487' : '34996434', 'SRR493036' : '21043986', 'SRR493097' : '31976667', 'SRR493098' : '13408363', 'SRR493101' : '7679343', 'SRR764885' : '50380962', 'SRR924656' : '39590367', 'SRR934391' : '36196662', 'SRR942022' : '17975524', 'SRR070570' : '8793425', 'SRR070571' : '8590680', 'SRR1001909' : '8168891', 'SRR1001910' : '8168891', 'SRR1019221' : '49462416', 'SRR345561' : '17838931', 'SRR345562' : '13627154', 'SRR346552' : '19200418', 'SRR346553' : '23724986', 'SRR394082' : '46284902', 'SRR504179' : '25512109', 'SRR504180' : '21115421', 'SRR504181' : '37241776', 'SRR515073' : '5196385', 'SRR515074' : '4527721', 'SRR527164' : '19992786', 'SRR527165' : '19917758', 'SRR584115' : '25097748', 'SRR584121' : '39243947', 'SRR584129' : '41360269', 'SRR584134' : '40452559', 'SRR653555' : '13572463', 'SRR653556' : '16154755', 'SRR653557' : '13556594', 'SRR653561' : '10241986', 'SRR653562' : '15917411', 'SRR653563' : '8824547', 'SRR653564' : '11800058', 'SRR653565' : '11623867', 'SRR653566' : '10246632', 'SRR653567' : '10750893', 'SRR653568' : '9057212', 'SRR653569' : '14316928', 'SRR653570' : '9656892', 'SRR653571' : '10805755', 'SRR653572' : '8849410', 'SRR653573' : '10559600', 'SRR653574' : '11134265', 'SRP018266' : '10916285', 'SRR653576' : '12643682', 'SRR653577' : '9781713', 'SRR653578' : '12201145', 'SRR797194' : '54048815', 'SRR797230' : '51421658', 'SRR833246' : '57084121', 'SRR847501' : '57084121', 'SRR847502' : '20633235', 'SRR1260032' : '41362473', 'SRR1260033' : '38879470', 'SRR1261509' : '46745857', 'SRR401413' : '13365743', 'SRR401414' : '9535671', 'SRR401415' : '15780686', 'SRR401416' : '16555068', 'SRR401417' : '11954841', 'SRR401418' : '19982775', 'SRR401419' : '13267215', 'SRR401420' : '9409649', 'SRR401421' : '15714100', 'ERR274309' : '29192485', 'SRR1046909' : '5254981', 'SRR1046910' : '5367327', 'SRR1524935' : '21855410', 'SRR1524938' : '16760164', 'SRR1524940' : '14685479', 'SRR314814' : '23367623', 'SRR949956' : '4537769', 'SRR949965' : '3984129', 'SRR949988' : '4955792', 'SRR949989' : '4717225'}

	abs_fpkm = mapped_reads / ((end-start) / 1000) / (float(reads_in_exp_dict[record]) / 1000000)

	# Output final data
	dumpJSON(200, locus, int(variant), chromosome, start, end, record, tissue, base64img.replace('\n',''), mapped_reads, abs_fpkm)

	'''
	dumpJSON(200, "AT2G24270", 1, 2, 10327035, 10329941, record, tissue, "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAyAQMAAAD1M0mrAAAABlBMVEX///8A/wDG5i4MAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABhklEQVRIie3VvUrFMBQH8MRKs9nRRczqpqOTEQSfQ/AFXAU1fZP7KsHZQZ/AQAcXweByC97bY3r6/ZV7UxAcbpYO//Nr03BOS8hu7db/WSfu+HI6OnfLm+nowS31H0i6ckszW07HwQwZFjJzy7GYKZQQe8uFRg/KV9LtJIzId0PONko6IgOYKw8hJXf5xSmDESkKKdySD+RBIWMivSTV5Bjl/YunDCr5+Gmldsu4Iw25QCnhWUIaOWVnS7eGPJUyAStfyVE73u/IzpaStcoaueaGiHZ8PS2XUMsl2GWIbO8JW7W8l4D2aPMlJJWESjIVljFFKcekAPjoSxPVEtsmLM+0K239V1+mXDGspTFObFScKYWOzIv7EqzE2sBKnUtTyrSBdFQuFMNTZFba4lNYbStBMXxKZGWWv9GKeshQFRLyQciuBpJNyW9upcilxmR7acUekQPJaxk5ZPAGffkj4kpyl4SBhGZahK/Us2X9a5G+svrM49F6SWhv1k/GTb/3ZLpBYlv+AhlEexWofYHkAAAAAElFTkSuQmCC", int(random.random()*1000), 0.999)
	'''

# The main program
if __name__ == '__main__':
	main()
