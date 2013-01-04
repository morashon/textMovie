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
SHOW = False
PRINT = False
MOVIE = False
WIDTH = 640
HEIGHT = 480
FPS = 24
FONTHEIGHT = 24
STALEDIR = 10
DIRCOLOR = "#dddddd"
AUDIO = None

argv = [sys.argv[0]]
for e in sys.argv[1:]:
    if e[:1] == "-":
        try:
            opt, val = e.split("=")
            try:
                val = int(val)
            except:
                try:
                    val = float(val)
                except:           
                    pass
        except:
            opt = e
            val = True
        print "setting", opt[1:].upper(), "=", val
        globals()[opt[1:].upper()] = val
    else:
        argv.append(e)
sys.argv = argv

try:
    SCRIPT = sys.argv[1]
    LENGTH = float(sys.argv[2])
    if len(sys.argv) > 3:
        AUDIO = sys.argv[3]
except:
    print "textMovie.py textfile.txt time [audiofile.wav]"
##    exit()

f = open(SCRIPT)
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
            key, value = block[0]   [1:-1].split('=')
            if key == 'time':
                nu['timestamp'] = float(value)
            else:
                print "unknown directive:", key
        else:
            nu['direction'] = block
    blocks[i] = nu

#add beginning and end stamps
blocks.insert(0, {'timestamp': 0.0})
if 'timestamp' not in blocks[-1]:
    if 'LENGTH' not in globals():
        print "Need to specify -LENGTH or add a final timestamp"
        exit()
    blocks.append({'timestamp': LENGTH})

def nextTimestamp(blocks, ix):
    chars = 0
    while 'timestamp' not in blocks[ix]:
        if 'dialogue' in blocks[ix]:
            for line in blocks[ix]['dialogue']:
                chars += len(line)
        ix += 1
    return blocks[ix]['timestamp'], chars
    
#compute times for each block & line
t = 0.0
t2, chars = nextTimestamp(blocks, 1)
mul = (t2 - t) / chars
for ix, block in enumerate(blocks):
    if 'timestamp' in block:
        if (t - block['timestamp']) > 0.0001:
            print "ERROR -- timestamp mismatch:", t, block['timestamp']
            exit()
        t = block['timestamp']
        block['time'] = t
        block['timestamp'] = t
        if ix + 1 < len(blocks):                            #ignore last timestamp"
            t2, chars = nextTimestamp(blocks, ix + 1)
            mul = (t2 - t) / chars
    else:
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

if PRINT:
    for block in blocks:
        print
        if 'dialogue' in block:
            print "%.2f" % block['time'],
            print "--------DIALOGUE--------"
            for i in range(len(block['dialogue'])):
                print "%.2f" % block['linetime'][i], block['dialogue'][i]
        elif 'direction' in block:
            print "%.2f" % block['time'],
            print "------DIRECTION--------"
            for line in block['direction']:
                print line
        elif 'timestamp' in block:
            print "%.2f" % block['time'],
            print "------TIMESTAMP--------"
            print block['timestamp']
        else:
            print "------UNKNOWN BLOCK TYPE-------"
            print block
if SHOW:
    cmd = "clear; xterm -e " + 'mplayer "' + AUDIO + '"&'
    print cmd
    os.system(cmd)
##    time.sleep(.1)

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
                print "%.2f" % block['time'],
                print "------DIRECTION-----"
                for line in block['direction']:
                    print line
            elif 'dialogue' in block:
                print "%.2f" % block['time'],
                print "------DIALOGUE-----"
                for j in range(len(block['dialogue'])):
                    line = block['dialogue'][j]
                    while (time.time() - T) < block['linetime'][j]:
                        time.sleep(.1)
                    print "%.2f" % block['linetime'][j], line
            elif 'timestamp' in block:
                print "%.2f" % block['time'],
                print "------TIMESTAMP--------"
                print block['timestamp']
            else:
                print "%.2f" % block['time'],
                print "------UNKNOWN BLOCK TYPE-------"
                print block
        time.sleep(.1)

if MOVIE:
    #let's make a movie! yay, yippie!
    import cv, cv2, numpy, Image, ImageFont, ImageDraw

    if AUDIO:
        ORIG = MOVIE
        MOVIE = MOVIE[:-4] + "_V.avi"

##    FOURCC = "DIVX"
    FOURCC = "HFYU"
    F4CC = cv.CV_FOURCC(FOURCC[0], FOURCC[1], FOURCC[2], FOURCC[3])    

    cvw = cv2.VideoWriter()
    cvw.open(MOVIE, F4CC, FPS, (WIDTH, HEIGHT))
    print cvw
    if not cvw.isOpened():
        print "FAIL"
        exit()

    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 24)
    pim = Image.new("RGB", (WIDTH, HEIGHT), (255,255,255))
    draw = ImageDraw.Draw(pim)
    cvim = cv.CreateImageHeader((WIDTH, HEIGHT), cv.IPL_DEPTH_8U, 3)
    cv.SetData(cvim, pim.tostring())
    im = numpy.asarray(cvim[:,:])

    frames = LENGTH * FPS
    ix = 0
    frame = 0
    lastdir = 0
    while ix < len(blocks):
        block = blocks[ix]
        t = frame / float(FPS)
        if t - lastdir > STALEDIR:                                  #erase directions after a bit
            lastdir = 10000000
            draw.rectangle((0,0,WIDTH,HEIGHT/2), fill=DIRCOLOR)
            cv.SetData(cvim, pim.tostring())
            im = numpy.asarray(cvim[:,:])
        if t >= block['time']:
            ix += 1
            if 'direction' in block:
                lastdir = t
                draw.rectangle((0,0,WIDTH,HEIGHT/2), fill=DIRCOLOR)
                for j in range(len(block['direction'])):
                    line = block['direction'][j]
                    draw.text((20, j * FONTHEIGHT), line, font=font, fill="black")
                cv.SetData(cvim, pim.tostring())
                im = numpy.asarray(cvim[:,:])
            if 'dialogue' in block:
                draw.rectangle((0,HEIGHT/2,WIDTH,HEIGHT), fill="white")
                for j in range(len(block['dialogue'])):
                    line = block['dialogue'][j]
                    draw.text((20, HEIGHT/2 + j * FONTHEIGHT), line, font=font, fill="black")
                cv.SetData(cvim, pim.tostring())
                im = numpy.asarray(cvim[:,:])
        cvw.write(im)
        frame += 1

    del cvw

    if AUDIO:
        cmd = "rm " + ORIG
        print cmd
        os.system(cmd)
        cmd = "avconv -i " + AUDIO + " -i " + MOVIE + " " + ORIG
        print cmd
        os.system(cmd)
        cmd = "rm " + MOVIE
        print cmd
        os.system(cmd)
