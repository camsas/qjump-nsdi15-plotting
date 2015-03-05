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
import numpy
import math

files=sys.argv[1:]

for file in files:
    #print "Working on", file, "..."
    #2014-01-17 00:17:44:954059, slv, 90e2bafffe27fc08/01, 0.000106986, 0.000002514, 0.000114000, 0.000114000, 11086
    times = []
    dropped = 0
    l = 0 
    for line in open(file):
        try:
            cols = line.split(",")

            ts = cols[0]
            (ymd,hmsus) = ts.split(" ")
            (h,m,s,us) = hmsus.split(":")
            ts =  int(h) * 60 * 60 # * 1000 * 1000 

            ts += int(m) * 60 #* 1000 * 1000
            ts += int(s) #* 1000 * 1000
            #ts += int(us) 
            if l == 0: 
                offset = ts
            ts -= offset
             
            sync = float(cols[4]) * 1000 * 1000
            if ts > 300:
                times.append(sync)

        except:
            dropped += 1 
            continue
        l += 1

    if len(times) == 0:
        #print "Failed on file %s" %(file)
        continue

    #Calculate the RMS sync offset
    sum_square = 0
    for t in times:
        sum_square += t * t
    mean_square = sum_square / len(times)
    rms = math.sqrt(mean_square)

    print "%f %i %i %s" % (rms, len(times), dropped, file)
