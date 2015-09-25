#!/usr/bin/python

import gd


graph = gd.image((200, 100))
white = graph.colorAllocate((255,255,255))
black = graph.colorAllocate((0,0,0))
graph.lines(((0, 50), (200, 50)), black)
f = open("test.png", "w")
graph.writePng(f)
f.close()