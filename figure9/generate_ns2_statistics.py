#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Malte Schwarzkopf
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
# * Neither the name of the project, the name of copyright holder nor the names 
#   of its contributors may be used to endorse or promote products derived from
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

import math
import sys, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from utils import *
from matplotlib import pylab
from fractions import Fraction
#from scipy.stats import scoreatpercentile

def get_ideal_fct(src, dst, num_pkts):
  switches = -1
  for block in range(0, 10):
    if (src >= 16 * block and src <= (16 * (block + 1)) - 1) and \
        (dst >= 16 * block and dst <= (16 * (block + 1)) - 1):
      switches = 1
      break
  if switches == -1:
    if src >= 0 and dst >= 0 and src <= 143 and dst <= 143:
      switches = 3
    else:
      print("WARNING: unreachable case for src=%d, dst=%d" % (src, dst))
      sys.exit(1)

  if switches == 1:
    ideal_fct = (((num_pkts -1 ) * 15 * 8 / 100.0) + 13.264) / 1000000  #0.000013264
  else:
    ideal_fct = (((num_pkts -1 ) * 15 * 8 / 100.0) + 14.680) / 1000000  #0.00001468
  return ideal_fct

#-------------------------------------

if len(sys.argv) < 2:
  print("usage: plot_ns2_flow_size_vs_variance.py <input dir1> <input1 label> " \
          "<input dir2> <input2 label> ... <output file>")
  sys.exit(1)

paper_mode = True

if paper_mode:
  set_paper_rcs()

# arg processing
if (len(sys.argv) - 1) % 2 == 1:
  # odd number of args, have output name
  outname = sys.argv[-1]
  print("Output name specified: %s" % (outname))
else:
  print("Please specify an output name!")
  sys.exit(1)

output_file = open(outname, 'w')
inputdirs = []
labels = []
for i in range(1, len(sys.argv)-1, 2):
  inputdirs.append(sys.argv[i])
  labels.append(sys.argv[i+1])

# parsing
#thresholds = [8760, 18980, 27740, 48180, 77380, 194180, 973820]
#thresholds = [10*1000, 100*1000, 1000*1000, 10*1000*1000]
thresholds = [10*1000, 10*1000*1000]
packet_size = 1500
j = 0
ideal_data = {}
for indir in inputdirs:
  print "---------------"
  print labels[j]
  print "---------------"
  binned_data = {}
  # Read data from flow.tr
  for line in open(indir).readlines():
    fields = [x.strip() for x in line.split()]
    if len(fields) != 5:
      continue
    num_pkts = Fraction(fields[0])
    flow_size = num_pkts * packet_size
    fct = Fraction(fields[1])
    num_lost = int(fields[2])
    src = int(fields[3])
    dst = int(fields[4])
    normed_fct = fct / get_ideal_fct(src, dst, num_pkts)

    bin_found = False
    # priority 7
    if flow_size <= thresholds[0]:
      append_or_create(binned_data, 0, normed_fct)
#      append_or_create(binned_data, 0, fct)
      bin_found = True
    # iterate over intermediate priorities
    for i in range(0, len(thresholds) - 1):
      if flow_size > thresholds[i] and flow_size <= thresholds[i+1]:
        append_or_create(binned_data, thresholds[i], normed_fct)
#        append_or_create(binned_data, thresholds[i], fct)
        bin_found = True
    # priority 0
    if not bin_found:
      append_or_create(binned_data, thresholds[len(thresholds) - 1], normed_fct)
#      append_or_create(binned_data, thresholds[len(thresholds) - 1], fct)
    append_or_create(binned_data, 1000000000000, normed_fct)

  if labels[j] == 'ideal':
    ideal_data = binned_data

  klist = binned_data.keys()
  klist.sort()
  #for t in klist:
  #  vals = binned_data[t]
  #  print "%d %d %f %f %f %f" % (t, len(vals), np.mean(vals), np.median(vals),
  #                               np.percentile(vals, 99), np.max(vals))
  num_region = 0
  for t in klist:
    num_region += 1
    if num_region > len(thresholds) + 1:
      break
    vals = binned_data[t]
    print >> output_file, "%s.tr region%d: %d flows" % (labels[j], num_region, len(vals))
  num_region = 0
  for t in klist:
    num_region += 1
    if num_region > len(thresholds) + 1:
      break
    vals = binned_data[t]
    perc99 = sorted(vals)[int(math.ceil( ((len(vals) - 1)  * .99)))]

    print >> output_file, "%s.tr region%d: 99%% %.6f mean %.6f" \
        % (labels[j], num_region, perc99, np.mean(vals))

  vals = binned_data[klist[3]]
  perc99 = sorted(vals)[ int(math.ceil( ((len(vals) -1) * .99)))]

  print >> output_file, "%s.tr allmean %.6f all99 %.6f" \
      % (labels[j], np.mean(vals), perc99)

  output_file.flush()


#  print "--"
#  for t in klist:
#    vals = binned_data[t]
#    print "%d %d %f %f %f %f" % (t, len(vals),
#                                 np.mean(vals) / np.mean(ideal_data[t]),
#                                 np.median(vals) / np.median(ideal_data[t]),
#                                 np.percentile(vals, 99) /
#                                 np.percentile(ideal_data[t], 99),
#                                 np.max(vals) / np.max(ideal_data[t]))


  j += 1
output_file.close()


# plotting
#fig = plt.figure(figsize=(2.33,1.66))
#plt.rc("font", size=7.0)
#fig, ax = plt.subplots()
#pos = np.array(range(len(binned_data)))+1
#bp = percentile_box_plot(ax, data)

# worst-case analytical approximation
#plt.plot(range(1, len(data)+1),
#         worst_case_approx(range(0, len(data)), train_length, pkt_size),
#         ':', color='r', label="modelled worst case", lw=1.0)

#plt.legend(loc=2, frameon=False)

#ax.set_xlabel('Number of hosts sending')
#ax.set_ylabel('Latency [$\mu$s]')
#plt.ylim(ymin=0)
#plt.xlim(0, len(inputdirs) + 1)

#plt.setp(bp['whiskers'], color='k',  linestyle='-' )
#plt.setp(bp['fliers'], markersize=3.0)
#plt.savefig(outname, format="pdf", bbox_inches='tight')
