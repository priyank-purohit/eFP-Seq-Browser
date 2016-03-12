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

# Make Image
def makeImage(filename, chromosome, start, end):
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

	highest_mapped_reads_count = highest_mapped_reads_count * 1.1 # To leave a little room at top of graph for Y-axis scale label...

	# Scale all y-axis values
	for i in range(len(values)):
		values[i] = int(values[i] / highest_mapped_reads_count * RNA_IMG_HEIGHT)


	# Create an image
	rnaseqgraph = gd.image((RNA_IMG_WIDTH, RNA_IMG_HEIGHT))
	white = rnaseqgraph.colorAllocate((255,255,255))
	green = rnaseqgraph.colorAllocate((0,255,0))
	black = rnaseqgraph.colorAllocate((0,0,0))
	gray = rnaseqgraph.colorAllocate((192,192,192))
	rnaseqgraph.filledRectangle((0, 5), (RNA_IMG_WIDTH, 5), gray) # max line at top

	# Actual RNA-Seq image
	for i in range(len(xvalues)):
		rnaseqgraph.rectangle((int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT), (int(float(xvalues[i] - start)/(end-start) * RNA_IMG_WIDTH), RNA_IMG_HEIGHT - values[i]), green)
	rnaseqgraph.string(0, (420, 5), str(int(highest_mapped_reads_count/1.1)), black) # y axis scale label

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
def dumpJSON(status, locus, variant, chromosome, start, end, record, tissue, base64img, reads_mapped_to_locus, pcc): # and svg_info that will be implemented later on
	print "Content-type: application/json\n"
	print json.dumps({"status": status, "locus": locus, "variant": variant, "chromosome": chromosome, "start": start, "end": end, "record": record, "tissue": tissue, "rnaseqbase64": base64img, "reads_mapped_to_locus": reads_mapped_to_locus, "pcc": pcc}) # and svg stuff
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
	base64img = makeImage(bam_file, chromosome, start, end)

	# Count the number of mapped reads to the locus
	lines = subprocess.check_output(['samtools', 'view', bam_file, region])
	mapped_reads = lines.count('Chr')

	# Output final data
	dumpJSON(200, locus, int(variant), chromosome, start, end, record, tissue, base64img.replace('\n',''), mapped_reads, 0.999)

	'''
	dumpJSON(200, "AT2G24270", 1, 2, 10327035, 10329941, record, tissue, "iVBORw0KGgoAAAANSUhEUgAAAcIAAAAyAQMAAAD1M0mrAAAABlBMVEX///8A/wDG5i4MAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABhklEQVRIie3VvUrFMBQH8MRKs9nRRczqpqOTEQSfQ/AFXAU1fZP7KsHZQZ/AQAcXweByC97bY3r6/ZV7UxAcbpYO//Nr03BOS8hu7db/WSfu+HI6OnfLm+nowS31H0i6ckszW07HwQwZFjJzy7GYKZQQe8uFRg/KV9LtJIzId0PONko6IgOYKw8hJXf5xSmDESkKKdySD+RBIWMivSTV5Bjl/YunDCr5+Gmldsu4Iw25QCnhWUIaOWVnS7eGPJUyAStfyVE73u/IzpaStcoaueaGiHZ8PS2XUMsl2GWIbO8JW7W8l4D2aPMlJJWESjIVljFFKcekAPjoSxPVEtsmLM+0K239V1+mXDGspTFObFScKYWOzIv7EqzE2sBKnUtTyrSBdFQuFMNTZFba4lNYbStBMXxKZGWWv9GKeshQFRLyQciuBpJNyW9upcilxmR7acUekQPJaxk5ZPAGffkj4kpyl4SBhGZahK/Us2X9a5G+svrM49F6SWhv1k/GTb/3ZLpBYlv+AhlEexWofYHkAAAAAElFTkSuQmCC", int(random.random()*1000), 0.999)
	'''

# The main program
if __name__ == '__main__':
	main()
