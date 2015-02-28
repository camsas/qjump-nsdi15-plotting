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

if len(sys.argv) < 3:
    print "Usage: do_hist <input_file> <bins>"
    sys.exit(-1)

bins_count = int(sys.argv[2])
nums = []
parse_errors = 0
range_errors = 0
for line in open(sys.argv[1]):
    try:
        num = int(line)
    except:
#        print line
        parse_errors += 1
        continue

    if num < 1 or num > 100000000000:
        range_errors += 1
        continue

    nums.append(num)

print "Parse errors found: %i" % (parse_errors)
print "Range errors found: %i" % (range_errors)

if len(nums) < 100:
    print "Fatal Error! Not enough points (%i)" % len(nums)
    sys.exit(-1)

nums.sort()

#min = numpy.min(nums)
#max = numpy.max(nums)
#print min,max
(ys,xs) = numpy.histogram(nums,bins=bins_count, range=[min(nums),max(nums)])
percent = [0,1,10,25,50,75,90,99,99.9, 99.99, 99.999, 99.9999, 99.99999, 99.999999, 100]

print "Total samples %i" % len(nums)
for p in percent:
    print "%3f%% - %ins" % (p, numpy.percentile(nums,p * 1.0))
    #print "%i" % (numpy.percentile(nums,p * 1.0))
print "Range = %ins" % (numpy.max(nums) - numpy.min(nums))

out = open("hist_out.ssv","w")
for i in range(0,len(ys)):
    out.write("%i %f\n" % (xs[i],ys[i] * 100.0 /len(nums)))



