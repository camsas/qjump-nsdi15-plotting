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

file=sys.argv[1]

dropped = 0

key_to_text = { \
    1 : "Alone", \
    2 : "Contended", \
    3 : "Qjump", \
    4 : "Eth Flow. Cnt",\
    5 : "DCTCP", \
  116 : "ECN-5:10", \
  117 : "ECN-10:20", \
  118 : "ECN-20:40", \
  119 : "ECN-40:80", \
  120 : "ECN-80:160", \
  122 : "ECN-160:320", \
  123 : "ECN-320:640", \
  124 : "ECN-640:12800", \
  125 : "ECN-1280:2560", \
  126 : "ECN-2560:5120", \
}   


#Map experiment ID's into experiment groups as above
mappings = {}
for i in range(0,7):
    mappings[i] = 1

for i in range(101,106):
    mappings[i] = 2

for i in range(106,111):
    mappings[i] = 3

for i in range(111,116):
    mappings[i] = 4

for i in range(116,121):
    mappings[i] = i

for i in range(122,127):
    mappings[i] = i

for i in range(127,132):
    mappings[i] = 5
    
averages = {}
for key in mappings:
    averages[key] = (0,0)

for line in open(file):
    try:
        (rms, found, dropped, fname) = line.split(" ")
        
    except:
        dropped += 1
        continue

    fname_parts = fname.split("_")
    id = int(fname_parts[-1])
    type = fname_parts[-2]
    mode = ""
    if len(fname_parts) >= 4:
        mode = fname_parts[-4]
    #Special cases
    if id == 100 or id == 121:
        continue #100 and 121 were globally broken, ignore

    if type == "PTPD" and id == 127:
        continue #Something is up with this result, doesn't make sense, will give DCTCP benefit of doubt

    if type == "PTPD" and id < 101 and mode == "hadoop":
        continue

    #Calculate average for each set of experiments    
    key = mappings[id]
    (avg,count) = averages[key]
    avg = (avg * count + float(rms)) / (count + 1)
    count += 1
    averages[key] = (avg,count)


vals = mappings.values()
vals = list(set(vals)) #get unique
for key in vals:
    print "%03i %-15s %f (%i)" % (key, key_to_text[key], averages[key][0], averages[key][1])



    
