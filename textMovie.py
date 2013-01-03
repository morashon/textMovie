#!/usr/bin/python

"""
Given a script text file and a sound file, read the script in sync

Basic idea: have time tags; implicit tags start with audio beg/end, but
we can add more using curly braces: {1:02:04.4) indicates that the following
line of dialogue occurs at that time

For now, a 'line' of dialogue is an actual line of text.  Actors names are
preceded with an underscore; names are included in the line.  Blank lines are
ignored.  Lines that follow immediately after an actor's line are considered
as spoken by that actor. Blocks of text with no actor prefix are considered
stage directions.
"""

import os, sys, time

try:
    tfile = sys.argv[1]
    afile = sys.argv[2]
except:
    print "textMovie.py textfile.txt time [audiofile.wav]"
    exit()

print "synchronizing " + tfile + " and " + afile

f = open(tfile)
lines = f.readlines()
f.close()

blocks = []
block = []

for line in lines:
    line = line.strip()
    if line != "":
        block.append(line)
    else:
        if len(block):
            blocks.append(block)
            block = []
if len(block):
    blocks.append(block)

for block in blocks:
    print "------BLOCK--------"
    for line in block:
        print line
