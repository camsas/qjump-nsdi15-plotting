#! /usr/bin/python

# Copyright (c) 2015, Matthew P. Grosvenor
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the project, the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import os
import numpy

#Make sure we get enough arguments
if len(sys.argv) < 2:
    sys.exit("Usage; ./process <files>")


files = sys.argv[1:]
#print "Processing", files
for f in files: 
    #print >> sys.stderr, "Now processing %s..." % f
    #q2pc_stats_rdp-ln.200000_202_20140426T090046.850167
    fn      = f.split("_")
    proto   = fn[2]
    wait    = fn[3]
    gid     = fn[4].split("T")[1].split(".")[0]

    t_global_start = 0
    global_lats = []
    rates = []
    
    i = 0
    lats = []
    for line in open(f):
        if i < 10:
            i += 1
            continue
        
        #2920 0 7 0 0 1398499276960049 1398499276960915 866 5
        try:
            (t_now, thread_id, client_id, srtos, crtos, t_sent, t_recvd, lat, ptype) = line[:-1].split(" ")
            t_now   = int(t_now)
            lat     = int(lat)
            t_sent  = int(t_sent)
            t_recvd = int(t_recvd)
        except:
            continue


        if t_now < 0:
            continue

        t_last = t_sent
               
        if i == 10:
            t_start = t_sent 
            t_global_start = t_sent

#        if i and i % 100:
#            print lat

        #if i > 10 and i % 1000 == 0:
        #    rate =  float(len(lats)) / (t_sent - t_start) * 1000 * 1000 / 2 / 7
        #    #print >> sys.stderr, t_sent, len(lats), t_sent - t_start, rate, numpy.median(lats) 
        #    print t_sent -1398499276960049 , len(lats), t_sent - t_start, rate, numpy.median(lats) 
        #    t_start = t_sent
        #    lats = []
        #    rates.append(rate)

        lats.append(lat)
        global_lats.append(lat)

        i += 1



    #print line
    #print "Processed", i, "samples"
    t_elapsed = t_last - t_global_start
    #print t_last
    #print t_start
    samples = float(len(global_lats))
    #print "Elapsed time =%i" % t_elapsed
    #print "Total packets =%i" % samples
    
    
    if not t_elapsed or not samples:
        continue
    
    
    rate = samples / t_elapsed * 1000 * 1000 / 2 / 7
    #print "Rate =", samples / t_elapsed * 1000 * 1000
    #print "Min,Med,Max", 
  

    out = [ "%-20s" % proto, \
            wait, \
            gid, \
            "%6i" %int(samples), \
            "%7ims" % (t_elapsed / 1000), \
            "%-5.2f" % rate, \
            str(numpy.min(global_lats)), \
            "%5.2fus" % numpy.median(global_lats), \
            str(numpy.max(global_lats))\
          ] #, "%5.2f" % (numpy.median(rates))]
    
    print "  ".join(out)
    sys.stdout.flush()
  #  print >> sys.stderr, "   ".join(out)
  #  sys.stderr.flush()

   
