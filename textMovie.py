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

afile = None
try:
    tfile = sys.argv[1]
    totime = float(sys.argv[2])
    if len(sys.argv) > 3:
        afile = sys.argv[3]
except:
    print "textMovie.py textfile.txt time [audiofile.wav]"
    exit()

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

#make each block an object
for i in range(len(blocks)):
    block = blocks[i]
    nu = {}
    if block[0][0] == '_':
        nu['dialogue'] = block
    else:
        nu['direction'] = block
    blocks[i] = nu

#compute length of dialogue in chars (later syls!)
totchars = 0
for block in blocks:
    if 'dialogue' in block:
        chars = 0
        for line in block['dialogue']:
            chars += len(line)
        block['chars'] = chars
        totchars += chars
print "total dialogue length:", totchars

#compute time stamps
mul = totime / totchars #factor to multiply to get time
print "mul factor:", mul
t = 0.0
for block in blocks:
    block['time'] = t
    if 'dialogue' in block:
        t += block['chars'] * mul

for block in blocks:
    print
    if 'dialogue' in block:
        print block['time'],
        print "--------DIALOGUE--------"
        for line in block['dialogue']:
            print line
    if 'direction' in block:
        print block['time'],
        print "------DIRECTION--------"
        for line in block['direction']:
            print line
print


