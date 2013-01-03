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

#compute total dialogue in chars (later syls!)
chars = 0
for block in blocks:
    if block[0][0] == '_':
        for line in block:
            chars += len(line)
print "total dialogue:", chars

#make each block an object
for i in range(len(blocks)):
    block = blocks[i]
    nu = {}
    if block[0][0] == '_':
        nu['dialogue'] = block
    else:
        nu['direction'] = block
    blocks[i] = nu

for block in blocks:
    print
    if 'dialogue' in block:
        print "--------DIALOGUE--------"
        for line in block['dialogue']:
            print line
    if 'direction' in block:
        print "------DIRECTION--------"
        for line in block['direction']:
            print line
print


