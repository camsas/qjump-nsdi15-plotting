#! /usr/bin/python

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
        num = float(line)
    except:
        parse_errors += 1
        continue

    if num < 0 or num > 1000000000:
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
percent = [0,1,10,25,50,75,90,99,100]

print "Total samples %i" % len(nums)
for p in percent:
    print "%3i%% - %fms" % (p, numpy.percentile(nums,p * 1.0))
    #print "%i" % (numpy.percentile(nums,p * 1.0))
print "Range = %fms" % (numpy.max(nums) - numpy.min(nums))

out = open("hist_out.ssv","w")
for i in range(0,len(ys)):
    out.write("%i %f\n" % (xs[i],ys[i] * 100.0 /len(nums)))



