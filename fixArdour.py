"""

That this is even necessary.

Ardour is exporting with glitches galore. This script looks at 3 exports and for each sample chooses the best 2 out of 3.
No I'm not kidding

"""


import os, sys
from scipy.io import wavfile

MAXSAMPLES=44100*30
THRESH = 100

##wav = wavfile.read("../seg1/export/seg1a_Session.wav")
##print len(wav), type(wav[1][0][0])
##exit()

def cmp(a, b):
    if abs(a - b) > THRESH:
        return False
    return True

def medianAndSpan(a, b, c):
    if a >= b >= c or c >= b >= a:
        return b, abs(c-a)
    if b >= c >= a or a >= c >= b:
        return c, abs(b-a)
    return a, abs(c-b)

#
# take 3 sample sets; make the first one a vote between all 3
#
def vote(*data):
    fails = 0                   #total fails -- leave alone but report
    votes = 0                   #contested (non-unanimous) votes
    n = len(d1[:MAXSAMPLES])
    for i in range(n):
        if (i % 44100) == 0:
            print "processing sample", i, "of", n, "%3.2f%%" % (float(i * 100) / n)
        for ch in range(2):
            samps = []
            for j in range(3):
                samp = data[j][i][ch]
                samps.append(samp)
            if samps[0] == samps[1] == samps[2]:        #speedup
                continue
            med, span = medianAndSpan(*samps)
            if span < THRESH:
                votes += 1
                samps[0] = med
                continue
            fails += 1
    return votes, fails

fn1 = sys.argv[1]
fn2 = sys.argv[2]
fn3 = sys.argv[3]
fout = sys.argv[4]

print "reading", fn1
typ, d1 = wavfile.read(fn1)
print "reading", fn2
typ, d2 = wavfile.read(fn2)
print "reading", fn3
typ, d3 = wavfile.read(fn3)

for d in [d1, d2, d3]:
    channels = len(d[0])
    typ = type(d[0][0])
    if channels != 2:
        print "stereo only"
        exit()
    if "numpy.int16" not in str(typ):
        print "wrong sample type"
        exit()

print "voting:"
votes, fails = vote(d1, d2, d3)
print "complete fails:", fails
print "contested votes:", votes
print "total samples:", len(d1)

print "writing"
wavfile.write(fout, 44100, d1)
