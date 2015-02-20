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
# * Neither the name of qjump-nsdi15-plotting nor the names of its
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


import os, sys, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from utils import *

#-----------
def serialize_hist(n, bins, outdir):
  nf = open(outdir + "/binvals.txt", "w")
  for val in n:
    nf.write(str(val)+"\n")

  bf = open(outdir + "/bins.txt", "w")
  for val in bins:
    bf.write(str(val)+"\n")
#-----------

if len(sys.argv) < 2:
  print "usage: plot_memcached_latency_cdfs.py <input file 1> <label 1> ... " \
      "<input  file n> <label n> [output file]"

paper_mode = True

if (len(sys.argv) - 1) % 2 != 0:
  outname = sys.argv[-1]
else:
  outname = "memcached_latency"

fnames = []
labels = []
for i in range(0, len(sys.argv) - 1, 2):
  fnames.append(sys.argv[1 + i])
  labels.append(sys.argv[2 + i])

if paper_mode:
  fig = plt.figure(figsize=(2.33,1.55))
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

if paper_mode:
  colors = paper_colors
else:
  colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', '0.5']

i = 0
for f in fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  j = 0
  minrto_outliers = 0
  values = {'GET': [], 'SET': [], 'TOTAL': []}
  for line in open(f).readlines():
    fields = [x.strip() for x in line.split()]
    if fields[0] not in ["GET", "SET", "TOTAL"]:
      print "Skipping line '%s'" % (line)
      continue
    req_type = fields[0]
    req_id = int(fields[1])
    req_delay = float(fields[2])
    if req_delay > 200000:
      minrto_outliers += 1
    values[req_type].append(req_delay)
    j += 1

  # info output
  print "--------------------------------------"
  print "%s (%s)" % (labels[i], f)
  print "--------------------------------------"
  print "%d total samples" % (j)
  print "%d outliers due to MinRTO" % (minrto_outliers)
  print "--------------------------------------"
  for t in ['TOTAL']:
    avg = np.mean(values[t])
    print "%s - AVG: %f" % (t, avg)
    median = np.median(values[t])
    print "%s - MEDIAN: %f" % (t, median)
    min_val = np.min(values[t])
    print "%s - MIN: %ld" % (t, min_val)
    max_val = np.max(values[t])
    print "%s - MAX: %ld" % (t, max_val)
    stddev = np.std(values[t])
    print "%s - STDEV: %f" % (t, stddev)
    print "%s - PERCENTILES:" % (t)
    perc1 = np.percentile(values[t], 1)
    print " 1st: %f" % (perc1)
    perc10 = np.percentile(values[t], 10)
    print " 10th: %f" % (np.percentile(values[t], 10))
    perc25 = np.percentile(values[t], 25)
    print " 25th: %f" % (np.percentile(values[t], 25))
    perc50 = np.percentile(values[t], 50)
    print " 50th: %f" % (np.percentile(values[t], 50))
    perc75 = np.percentile(values[t], 75)
    print " 75th: %f" % (np.percentile(values[t], 75))
    perc90 = np.percentile(values[t], 90)
    print " 90th: %f" % (np.percentile(values[t], 90))
    perc99 = np.percentile(values[t], 99)
    print " 99th: %f" % (np.percentile(values[t], 99))

#  print "COPYABLE:"
#  print avg
#  print stddev
#  print max_val
#  print min_val
#  print perc1
#  print perc10
#  print perc25
#  print perc50
#  print perc75
#  print perc90
#  print perc99

    # figure out number of bins based on range
    bin_width = 1  # 7.5ns measurement accuracy
    bin_range = max_val - min_val
    num_bins = min(250000, bin_range / bin_width)

    print "Binning into %d bins and plotting..." % (num_bins)

    # plotting
    if paper_mode:
  #    plt.rc("font", size=8.0)
      label_str = labels[i]
      if i % 3 == 0:
        style = 'solid'
      elif i % 3 == 1:
        style = 'dashed'
      else:
        style = 'dotted'
      (n, bins, patches) = plt.hist(values[t], bins=num_bins, log=False, normed=True,
                                    cumulative=True, histtype="step",
                                    ls=style, color=colors[i])
      # hack to add line to legend
      plt.plot([-100], [-100], label=labels[i],
               color=colors[i],
               linestyle=style, lw=1.0)
      # hack to remove vertical bar
      patches[0].set_xy(patches[0].get_xy()[:-1])
    #  serialize_hist(n, bins, os.path.dirname(outname))
    else:
      label_str = "%s (%s)" % (labels[i], t)
      (n, bins, patches) = plt.hist(values[t], bins=num_bins, log=False, normed=True,
                                    cumulative=True, histtype="step",
                                    label=label_str)
      # hack to remove vertical bar
      patches[0].set_xy(patches[0].get_xy()[:-1])
  #  serialize_hist(n, bins, os.path.dirname(outname))

  i += 1

plt.xticks()
#  plt.xscale("log")
plt.xlim(0, 2250)
plt.xticks(range(0, 2500, 500), [str(x) for x in range(0, 2500, 500)])
plt.ylim(0, 1.0)
plt.yticks(np.arange(0.0, 1.01, 0.2), [str(x) for x in np.arange(0.0, 1.01, 0.2)])
plt.xlabel("Request latency [$\mu$s]")
#print n
#print bins
#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
#           ncol=3, mode="expand", frameon=True, borderaxespad=0.)
plt.legend(loc=4, frameon=False, handlelength=2.5, handletextpad=0.2)

plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches="tight")

plt.ylim(0.9, 1.0)
#plt.axhline(0.999, ls='--', color='k')

plt.savefig("%s-90th.pdf" % outname, format="pdf", bbox_inches="tight")
