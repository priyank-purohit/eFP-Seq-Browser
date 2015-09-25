import urllib2
import re

print urllib2.urlopen("http://trace.ncbi.nlm.nih.gov/Traces/study/?acc=ERR274311&go=go").read()

