#!/usr/bin/python
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<title>hello world</title>"

import cgi
import cgitb
cgitb.enable()

print "<body>"

#Naturally, 0xff0000 is a lower number than 0xffff00... remember your hex!
#But this doesn't work for us! 0xff0000 is red... which is our max colour! while 0xffff00 is yellow, which our min colour...
#we need to reverse this then. There are multiple ways to do this... we could do 0xffff00 - percentage_of_max!
min_colour = 0xffff00 - 0x0000 #0xffff00 minus 0
medium_colour = 0xffff00 - (0xff00 * 0.5)
max_colour = 0xffff00 - 0xff00
print "0% is"
print "<span style='color:%20x'>this colour</span> <br />" % min_colour #the %02x translates the number into hex...
print "50% is "
print "<span style='color:%20x'>this colour</span> <br />" % medium_colour
print "100% is "
print "<span style='color:%20x'>this colour</span> <br />" % max_colour
print "</body>"
