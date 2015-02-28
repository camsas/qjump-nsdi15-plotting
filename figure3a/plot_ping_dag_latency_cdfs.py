#! /usr/bin/python

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


# Simple script which takes a file with one ping latency (expressed as a
# signed integer) per line and plots a trivial histogram.

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
  print "usage: plot_ping_latency_cdfs.py <input file 1> <label 1> ... " \
      "<input  file n> <label n> [output file]"

paper_mode = True

if (len(sys.argv) - 1) % 2 != 0:
  outname = sys.argv[-1]
  del sys.argv[-1]
else:
  outname = "ping_dag_latency"

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
#  colors[2] = paper_colors[1]
#  colors[1] = paper_colors[3]
else:
  colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', '0.5']

i = 0
values = []
for f in fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  j = 0
  values.append([])
  for line in open(f).readlines():
    delay = float(line.strip())
    values[i].append(delay)
    j += 1

  # info output
  print "--------------------------------------"
  print "%s (%s)" % (labels[i], f)
  print "--------------------------------------"
  print "%d total samples" % (j)
  print "--------------------------------------"
  avg = np.mean(values[i])
  print "AVG: %f" % (avg)
  median = np.median(values[i])
  print "MEDIAN: %f" % (median)
  min_val = np.min(values[i])
  print "MIN: %ld" % (min_val)
  max_val = np.max(values[i])
  print "MAX: %ld" % (max_val)
  stddev = np.std(values[i])
  print "STDEV: %f" % (stddev)
  print "PERCENTILES:"
  perc1 = np.percentile(values[i], 1)
  print " 1st: %f" % (perc1)
  perc10 = np.percentile(values[i], 10)
  print " 10th: %f" % (np.percentile(values[i], 10))
  perc25 = np.percentile(values[i], 25)
  print " 25th: %f" % (np.percentile(values[i], 25))
  perc50 = np.percentile(values[i], 50)
  print " 50th: %f" % (np.percentile(values[i], 50))
  perc75 = np.percentile(values[i], 75)
  print " 75th: %f" % (np.percentile(values[i], 75))
  perc90 = np.percentile(values[i], 90)
  print " 90th: %f" % (np.percentile(values[i], 90))
  perc99 = np.percentile(values[i], 99)
  print " 99th: %f" % (np.percentile(values[i], 99))

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

  i += 1

i = 0
a = plt.axes([0., 0., .4, 1.])
for i in range(len(values)):
  # figure out number of bins based on range
  print len(values[i])
  min_val = np.min(values[i])
  max_val = np.max(values[i])
  bin_width = 1  # 7.5ns measurement accuracy
  bin_range = max_val - min_val
  num_bins = min(2500, bin_range / bin_width)
  print "Binning into %d bins and plotting..." % (num_bins)

  if paper_mode:
    if i % 3 == 0:
      style = 'solid'
    elif i % 3 == 1:
      style = 'dashed'
    else:
      style = 'dotted'
  if i < 3:
    (n, bins, patches) = plt.hist(values[i], bins=num_bins, log=False, normed=True,
                                  cumulative=True, histtype="step",
                                  linestyle=style, color=colors[i])
    patches[0].set_xy(patches[0].get_xy()[:-1])
plt.xlim(0, 5000)
plt.xticks([0, 1000, 2000, 3000, 4000], ['0', '1', '2', '3', '4'], ha='left')
plt.ylim(0, 1.0)
plt.yticks(np.arange(0, 1.01, 0.2), [str(x) for x in np.arange(0, 1.01, 0.2)])


a = plt.axes([.4, 0., .6, 1.])
i = 0
for i in range(len(values)):
  # figure out number of bins based on range
  min_val = np.min(values[i])
  max_val = np.max(values[i])
  bin_width = 1  # 7.5ns measurement accuracy
  bin_range = max_val - min_val
  num_bins = min(2500, bin_range / bin_width)
  print "Binning into %d bins and plotting..." % (num_bins)

  # plotting
  if paper_mode:
    if i % 3 == 0:
      style = 'solid'
    elif i % 3 == 1:
      style = 'dashed'
    else:
      style = 'dotted'
#    plt.rc("font", size=8.0)
    (n, bins, patches) = plt.hist(values[i], bins=num_bins, log=False, normed=True,
                                  cumulative=True, histtype="step",
                                  linestyle=style, color=colors[i])
    # hack to remove vertical bar
    patches[0].set_xy(patches[0].get_xy()[:-1])
    # hack to add line to legend
    plt.plot([-100], [-100], label=labels[i],
             color=colors[i % len(colors)],
             linestyle=style, lw=1.0)

  #  serialize_hist(n, bins, os.path.dirname(outname))
  else:
    (n, bins, patches) = plt.hist(values[i], bins=num_bins, log=False, normed=True,
                                  cumulative=True, histtype="step",
                                  label=labels[i])
    # hack to remove vertical bar
    patches[0].set_xy(patches[0].get_xy()[:-1])
  #  serialize_hist(n, bins, os.path.dirname(outname))

plt.xticks([6000, 300000, 600000, 900000, 1200000],
           [5, 300, 600, 900, 1200])

#plt.xlim(-100000, 1350000)
plt.xlim(6000, 1350000)
plt.ylim(0, 1.0)
plt.yticks(np.arange(0, 1.01, 0.2), ['' for x in np.arange(0, 1.01, 0.2)])
plt.xlabel("Latency in $\mu$s", x=0.1)
#plt.legend(bbox_to_anchor=(-0.8, 1.02, 1.8, .102), loc=3, handletextpad=0.2,
#           ncol=3, mode="expand", frameon=True, borderaxespad=0., handlelength=2.5)
plt.legend(loc='upper left', handletextpad=0.2, mode="expand", frameon=True,
           borderaxespad=0.2, handlelength=2.5)
leg = plt.gca().get_legend()
frame = leg.get_frame()
frame.set_edgecolor('1.0')
frame.set_alpha(0.0)

fig.set_size_inches(1.9, 1.22)
plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches='tight')

#plt.ylim(0.99, 1.0)
#plt.axhline(0.999, ls='--', color='k')

#plt.savefig("%s-99th.pdf" % outname, format="pdf", bbox_inches="tight")
