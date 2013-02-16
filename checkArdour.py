#!/usr/bin/python

"""
check this directory's ardour and .wav timestamps for up-to-dateness
"""

import os, sys, time
MAXT = 3600*2

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
if mx < MAXT:
    print "looks up to date; max time:", mx / 3600., "hours"
else:
    print "needs RECOMPILE! max time:", mx / 3600., "hours"
