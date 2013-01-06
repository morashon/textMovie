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
FONTHEIGHT = 44
LEFTOFFSET = 20
STALEDIR = 10
DIRCOLOR = "#dddddd"
AUDIO = None
DEBUG = False

def splitLine(line, draw, font):
    def width(s):
        w, h = draw.textsize(s, font=font)
        return w
    words = line.split()
    lines = []
    while len(words) > 0:
        t = ""
        while len(words) > 0 and width(t) <= WIDTH*2-LEFTOFFSET:
            if width(t + " " + words[0]) > WIDTH*2-LEFTOFFSET:
                break
            t += words.pop(0) + " "
        if t == "":
            print "ERROR - splitLine failure"
            exit()
        lines.append(t.rstrip())
    return lines

i = 1
while i < len(sys.argv):
    e = sys.argv[i]
    if e[:1] != "-":
        break
    opt = e[1:]
    if len(sys.argv) > i+1:                     #if there's a next arg
        nxt = sys.argv[i+1]
    else:
        nxt = '-'                               #fake opt for flag at end
    try:
        val = int(nxt)                          #and it's numeric, OK
        i += 2
    except:
        try:
            val = float(nxt)                    #or float
            i += 2
        except:
            if nxt[0:1] != '-':                 #or a non-option string
                val = nxt
                i += 2
            else:
                val = True                      #otherwise assume flag; don't eat arg
                i += 1

    print "setting", opt.upper(), "=", val
    globals()[opt.upper()] = val

try:
    f = open(SCRIPT)
    lines = f.readlines()
    f.close()
except:
    print "textMovie.py -option [VALUE]"
    print "required options: -script"
    print "optional options: -audio FILENAME, -movie OUTPUTFILENAME, -length SECONDS, -print, -show, -fps"
    print "in fact, any global var in caps can be set as an option, like STALEDIR, if you know what I mean"
    exit()

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
the_actor = None
for i in range(len(blocks)):
    if DEBUG:
        print
        for e in block:
            print e
    block = blocks[i]
    nu = {}
    while block[0][0] == "{":
        key, value = block[0][1:-1].split('=')
        if key == 'nudge':
            if len(block) <= 1:
                print "ERROR - nudge directive must be at top of a block - block:", i, block
                exit()
            nu['nudge'] = float(value)
            block.pop(0)                                    #a nudge modifies a block's time
        elif key == 'hold':
            if len(block) <= 1:
                print "ERROR - hold directive must be at top of a block - block:", i, block
                exit()
            nu['hold'] = float(value)
            block.pop(0)                                    #a nudge modifies a block's time
        elif key == 'time':
            nu['timestamp'] = float(value)
            blocks[i] = nu
            if len(block) > 1:
                print "ERROR -- time directive should be its own block:"
                print block[1:]
                exit()
            break                                            #timestamps are their own blocks
        else:
            print "ERROR: unknown directive:", key, value
            exit()

    if 'timestamp' in nu:
        continue

    if block[0][0] == '_':
        nu['dialogue'] = block
        if block[0] == "_":
            block.pop(0)                                    #lonely underscore just means continue dialog
        else:
            brk = block[0].find(":")                        #first word followed by colon is actor name
            if brk >= 0:
                the_actor = block[0][1:brk].replace(':', '')
                block[0] = block[0][brk+2:]
            else:                                           #just remove underscore
                block[0] = block[0][1:]
        if the_actor:
            nu['actor'] = the_actor
    else:
        nu['direction'] = block
    blocks[i] = nu

print "LAST BLOCK:", blocks[-1]
#add beginning and end stamps
blocks.insert(0, {'timestamp': 0.0})
if 'timestamp' not in blocks[-1]:
    if 'LENGTH' not in globals():
        print "Need to specify -LENGTH or add a final timestamp"
        exit()
    blocks.append({'timestamp': LENGTH})
else:
    LENGTH = blocks[-1]['timestamp']

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
if chars:
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
            if chars:
                mul = (t2 - t) / chars                      #if chars==0, no dialog before next stamp
    else:
        nudge = 0
        if 'nudge' in block:
            nudge = block['nudge']
        block['time'] = t + nudge
        if 'dialogue' in block:
            block['linetime'] = []
            for line in block['dialogue']:
                block['linetime'].append(t + nudge)
                t += len(line) * mul

#re sort by time; nudge may have moved things to illogical places
def key(x):
    return x['time']            #never liked lambda
blocks.sort(key=key)

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
            if 'actor' in block:
                print block['actor'] + ":"
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
                if 'actor' in block:
                    print block['actor'] + ":"
                for j in range(len(block['dialogue'])):
                    line = block['dialogue'][j]
                    if SHOW == "lines":
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
        MOVIE = MOVIE[:MOVIE.rfind('.')] + "_V.avi"
        print "intermediate file:", MOVIE
        print "final output file:", ORIG

    FOURCC = "DIVX"
##    FOURCC = "HFYU"
    F4CC = cv.CV_FOURCC(FOURCC[0], FOURCC[1], FOURCC[2], FOURCC[3])    

    cvw = cv2.VideoWriter()
    cvw.open(MOVIE, F4CC, FPS, (WIDTH, HEIGHT))
    print cvw
    if not cvw.isOpened():
        print "FAIL"
        exit()

    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", FONTHEIGHT)
    pim = Image.new("RGB", (WIDTH*2, HEIGHT*2), (255,255,255))
    draw = ImageDraw.Draw(pim)
    cvim = cv.CreateImageHeader((WIDTH, HEIGHT), cv.IPL_DEPTH_8U, 3)
    pim2 = pim.resize((WIDTH, HEIGHT), Image.BILINEAR)
    cv.SetData(cvim, pim2.tostring())
    im = numpy.asarray(cvim[:,:])

    frames = LENGTH * FPS
    ix = 0
    frame = 0
    lastdir = 0
    dirhold = STALEDIR
    lastdia = 0
    diahold = 999
    while ix < len(blocks):
        block = blocks[ix]
        t = frame / float(FPS)
        if t - lastdir > dirhold:                                  #erase directions after a bit
            lastdir = 10000000
            draw.rectangle((0,0,WIDTH*2,HEIGHT), fill=DIRCOLOR)
            pim2 = pim.resize((WIDTH, HEIGHT), Image.BILINEAR)
            cv.SetData(cvim, pim2.tostring())
            im = numpy.asarray(cvim[:,:])
        if t - lastdia > diahold:                                  #erase dialogue after a bit more
            lastdia = 10000000
            draw.rectangle((0,HEIGHT,WIDTH*2,HEIGHT*2), fill="white")
            pim2 = pim.resize((WIDTH, HEIGHT), Image.BILINEAR)
            cv.SetData(cvim, pim2.tostring())
            im = numpy.asarray(cvim[:,:])
        if t >= block['time']:
            ix += 1
            if 'direction' in block:
                lastdir = t
                if 'hold' in block:
                    dirhold = block['hold']
                else:
                    dirhold = STALEDIR
                draw.rectangle((0,0,WIDTH*2,HEIGHT), fill=DIRCOLOR)
                k = 0
                for j in range(len(block['direction'])):
                    line = block['direction'][j]
                    lines = splitLine(line, draw, font)
                    for line in lines:
                        if k * FONTHEIGHT > (HEIGHT-FONTHEIGHT-4):
                            print "ERROR -- too much text"
                            exit()
                        draw.text((LEFTOFFSET, k * FONTHEIGHT), line, font=font, fill="black")
                        k += 1
                pim2 = pim.resize((WIDTH, HEIGHT), Image.BILINEAR)
                cv.SetData(cvim, pim2.tostring())
                im = numpy.asarray(cvim[:,:])
            if 'dialogue' in block:
                lastdia = t
                if 'hold' in block:
                    diahold = block['hold']
                else:
                    diahold = 999
                draw.rectangle((0,HEIGHT,WIDTH*2,HEIGHT*2), fill="white")
                k = 0
                if 'actor' in block:
                    draw.text((LEFTOFFSET, HEIGHT), block['actor'] + ':', font=font, fill="#0000ff")
                    k = 1
                for j in range(len(block['dialogue'])):
                    line = block['dialogue'][j]
                    lines = splitLine(line, draw, font)
                    for line in lines:
                        if k * FONTHEIGHT > (HEIGHT-FONTHEIGHT-4):
                            print "ERROR -- too much text"
                            exit()
                        draw.text((LEFTOFFSET, HEIGHT + k * FONTHEIGHT), line, font=font, fill="black")
                        k += 1
                pim2 = pim.resize((WIDTH, HEIGHT), Image.BILINEAR)
                cv.SetData(cvim, pim2.tostring())
                im = numpy.asarray(cvim[:,:])
        cvw.write(im)
        frame += 1

    del cvw

    if AUDIO:
        cmd = "rm " + ORIG
        print cmd
        os.system(cmd)
        cmd = "avconv -i " + AUDIO + " -i " + MOVIE + " -acodec libmp3lame -ab 256k " + ORIG
        print cmd
        os.system(cmd)
        cmd = "rm " + MOVIE
        print cmd
        os.system(cmd)
