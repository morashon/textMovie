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
        if block[0][0] == '{':
            nu['timestamp'] = block
        else:
            nu['direction'] = block
    blocks[i] = nu

#add beginning and end stamps
blocks.insert(0, {'timestamp': [0.0]})
blocks.append({'timestamp': [totime]})

#compute length of dialogue in chars (later syls!)
totchars = 0
for block in blocks:
    if 'dialogue' in block:
        chars = 0
        for line in block['dialogue']:
            chars += len(line)
        totchars += chars
print "total dialogue length:", totchars

def nextTimestamp(blocks, ix):
    while 'timestamp' not in blocks[ix]:
        ix += 1
    return blocks[ix]['timestamp'][0]
    
#compute times for each block & line
t = 0.0
t2 = nextTimestamp(blocks, 1)
mul = (t2 - t) / totchars
for block in blocks:
    block['time'] = t
    if 'dialogue' in block:
        block['linetime'] = []
        for line in block['dialogue']:
            block['linetime'].append(t)
            t += len(line) * mul

#fix direction stamps to be interpolated
##for i in range(1, len(blocks)-1, 1):            #ignore first and last
##    block = blocks[i]
##    if 'direction' in block:
##        tm1 = blocks[i-1]['time']
##        tp1 = blocks[i+1]['time']
##        t = (tm1 + tp1) * .5
##        block['time'] = t

if not afile:
    for block in blocks:
        print
        if 'dialogue' in block:
            print block['time'],
            print "--------DIALOGUE--------"
            for i in range(len(block['dialogue'])):
                print block['linetime'][i], block['dialogue'][i]
        if 'direction' in block:
            print block['time'],
            print "------DIRECTION--------"
            for line in block['direction']:
                print line
        if 'timestamp' in block:
            print block['time'],
            print "------TIMESTAMP--------"
            print block['timestamp'][0]
else:
    cmd = "clear; xterm -e " + 'mplayer "' + afile + '"&'
    print cmd
    os.system(cmd)
    time.sleep(1)

    print "\n" * 60
    print "---------------BEGIN------------------"

    T = time.time()

    ix = 0
    while ix < len(blocks):
        block = blocks[ix]
        t = time.time() - T
        if t >= block['time']:
            print
            ix += 1
            if 'direction' in block:
                print "------DIRECTION-----"
                for line in block['direction']:
                    print line
            if 'dialogue' in block:
                print "------DIALOGUE-----"
                for j in range(len(block['dialogue'])):
                    line = block['dialogue'][j]
                    while (time.time() - T) < block['linetime'][j]:
                        time.sleep(.1)
                    print line
        time.sleep(.1)
