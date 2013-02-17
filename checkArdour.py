#!/usr/bin/python

"""
check this directory's ardour and .wav timestamps for up-to-dateness
"""

import os, sys, time
MAXT = 3600*5

path = os.path.abspath(".")
segname = os.path.basename(path)
print segname,

ta = os.path.getmtime("export/SEGa_Session.wav".replace("SEG", segname))
tb = os.path.getmtime("export/SEGb_Session.wav".replace("SEG", segname))
tc = os.path.getmtime("export/SEGc_Session.wav".replace("SEG", segname))
t_ = os.path.getmtime("export/SEG_Session.wav".replace("SEG", segname))
tr = os.path.getmtime("SEG.ardour".replace("SEG", segname))

##print ta,tb,tc,t_,tr

mx = max(t_, ta, tb, tc, tr) - min(t_, ta, tb, tc, tr)
chk = True
if t_ < ta:
    print "_Session older than a_Session",
    chk = False
if t_ < tb:
    print "_Session older than b_Session",
    chk = False
if t_ < tc:
    print "_Session older than c_Session",
    chk = False
if t_ < tr:
    print "_Session older than ardour",
    chk = False

if mx > MAXT:
    print "suspicious:", mx / 3600., "hours",
if chk == True:
    print "looks up to date!"
else:
    print "needs RECOMPILE!"
