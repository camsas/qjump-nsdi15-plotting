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
import numpy
import os

if len(sys.argv) < 2:
    print "Usage ./process_mem <directory>"
    sys.exit(-1)

dirs=sys.argv[1:]

i = 0
ts_start = 0
found_total = 0
dropped_total = 0
ts_prev = 0
lts_total = 0
lts_count = 0
sum_square_error = 0
sum_square = 0
for directory in dirs:    
    ts_start = 0
    found_total = 0
    dropped_total = 0
    ts_prev = 0
    lts_total = 0
    lts_count = 0
    print >> sys.stderr, "Working on %s" % directory
    #for f in os.listdir(directory): 
    values = []
    file_out = open(directory + ".set.processed2", "w" ) 
    for i in range(1,26):
  
         try:
            fname =  directory + "/" + directory + ".%02d" % i 
            #print >> sys.stderr, "Opening on %s" % fname
            data_file = open(fname) 
         except:
            print >> sys.stderr, "Can't open %s" % fname
            continue

         print >> sys.stderr, "Working on %s" % fname
         for line in data_file:
            if dropped_total and (dropped_total % 1000000  == 0):
                print "Dropped %ik so far..." % (dropped_total / 1000)

            try:
                cols = line.split(" ")
                #TOTAL 0 1390395616147117616 910
                ts = int(cols[2])
                lt = int(cols[3])
                ty = cols[0]

                if ty != "SET":
                    dropped_total += 1
                    continue
                #if lt < 150000:
                values.append(lt)
            except:
                dropped_total += 1
                continue


            if i and (i % 1000000 == 0):
                print >> sys.stderr, "Processed %ik so far..." % (i / 1000)
                #mean_square_error = sum_square_error / found_total
                #mean_square = sum_square / found_total
                #rmse = math.sqrt(mean_square_error)
                #rms = math.sqrt(mean_square)
                #avg = numpy.mean(values)
                #stdev = numpy.std(values)
                #perc99 = numpy.percentile(values, 99)
                #print "avg: %10.2f 99th: %10.2f stdev: %10.2f RMSE=%10.2fus RMS=%10.2fus SSE=%i MSE=%i found=%i dropped=%i (%s)" \
                #    % (avg, perc99, stdev, rmse, rms,  sum_square_error, mean_square_error, found_total, dropped_total, file)
                #sys.stdout.flush()


            if not ts_start:
                ts_start = ts

            #print ts, ts - ts_start

            if (ts - ts_start)/ 1000.0 / 1000.0 / 1000.0 > ts_prev + 0.25:
                #print "%f %f" % ( ts_prev, lts_total * 1.0 / lts_count )
                file_out.write("%f %f\n" % ( ts_prev, lts_total * 1.0 / lts_count ) )     
                ts_prev = (ts - ts_start)/ 1000.0 / 1000.0 / 1000.0
                lts_total = 0
                lts_count = 0

            sum_square_error += (lt - 443 ) * (lt- 443)
            sum_square += (lt ) * (lt)

            found_total += 1
            i += 1
            lts_count += 1
            lts_total += lt



    file_out.write("-----------------------------------\n")

    count = len(values)    

    if(count == 0): 
        continue

    stddev = numpy.std(values) 
    mean = numpy.mean(values)
    p0   = numpy.percentile(values,0) 
    p50  = numpy.percentile(values,50)
    p99  = numpy.percentile(values,99)
    p999  = numpy.percentile(values,99.9)
    p9999  = numpy.percentile(values,99.99)
    p100 = numpy.percentile(values,100)
    
    mean_square_error = sum_square_error / found_total
    mean_square = sum_square / found_total
    rmse = math.sqrt(mean_square_error)
    rms = math.sqrt(mean_square)
         
    file_out.write( "MEMD, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (directory, count, p0, mean, stddev, p50, p99, p999, p9999, p100, rms, rmse) )
    print "MEMD, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (directory, count, p0, mean, stddev, p50, p99, p999, p9999, p100, rms, rmse) 



 
