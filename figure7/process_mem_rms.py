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
import math
import os

if len(sys.argv) < 3:
    print "Usage ./process_mem <TOTAL|SET|GET> <directory>"
    sys.exit(-1)

rec_type = sys.argv[1]
data_dir = sys.argv[2]
files= os.listdir(data_dir)

i = 0
ts_start = 0
found_total = 0
dropped_total = 0
ts_prev = 0
times = []
for file in files:
    #print "Working on", file, "..."
    lts_total = 0
    lts_count = 0
    for line in open(data_dir + "/" + file):
        if dropped_total and (dropped_total % 1000000  == 0):
            print "Dropped %ik so far..." % (dropped_total / 1000)
        try:
	    cols = line.split(" ")
            #TOTAL 0 1390395616147117616 910
            ts = int(cols[2])
            lt = int(cols[3])
            ty = cols[0]
        except:
            dropped_total += 1
            continue

        if not ty == rec_type:
            dropped_total += 1
            continue

        if i and (i % 100000 == 0):
            print "Processed %ik so far..." % (i / 1000)

        found_total += 1
        times.append(lt)

        i += 1

print "Found   : %i records" % found_total
print "Dropped : %i records" % dropped_total

if len(times) == 0:
    print "Failed on directory %s" %(data_dir)

sum_square = 0
for t in times:
    sum_square += t * t

mean_square = sum_square / len(times)
rms = math.sqrt(mean_square)
print "%f %i %i %s" % (rms, len(times), dropped_total, data_dir)
