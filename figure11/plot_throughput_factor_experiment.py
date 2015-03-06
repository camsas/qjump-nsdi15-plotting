#!/usr/bin/python
# -*- coding: utf-8 -*-
# Simple script which takes a file with one packet latency (expressed as a
# signed integer) per line and plots a trivial histogram.

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
from scipy.stats import scoreatpercentile

pkt_size = 256
train_length = 6

# @author: Aaron Blankstein, with modifications by Malte Schwarzkopf
class boxplotter(object):
    def __init__(self, median, top, bottom, whisk_top=None,
                 whisk_bottom=None, extreme_top=None):
        self.median = median
        self.top = top
        self.bott = bottom
        self.whisk_top = whisk_top
        self.whisk_bott = whisk_bottom
        self.extreme_top = extreme_top
    def draw_on(self, ax, index, box_color = "blue",
                median_color = "red", whisker_color = "black"):
        width = .7
        w2 = width / 2
        ax.broken_barh([(index - w2, width)],
                       (self.bott,self.top - self.bott),
                       facecolor="white",edgecolor=box_color, lw=0.5)
        ax.broken_barh([(index - w2, width)],
                       (self.median,0),
                       facecolor="white", edgecolor=median_color, lw=0.5)
        if self.whisk_top is not None:
            ax.broken_barh([(index - w2, width)],
                           (self.whisk_top,0),
                           facecolor="white", edgecolor=whisker_color, lw=0.5)
            ax.broken_barh([(index , 0)],
                           (self.whisk_top, self.top-self.whisk_top),
                           edgecolor=box_color,linestyle="solid", lw=0.5)
        if self.whisk_bott is not None:
            ax.broken_barh([(index - w2, width)],
                           (self.whisk_bott,0),
                           facecolor="white", edgecolor=whisker_color, lw=0.5)
            ax.broken_barh([(index , 0)],
                           (self.whisk_bott,self.bott-self.whisk_bott),
                           edgecolor=box_color,linestyle="solid", lw=0.5)
        if self.extreme_top is not None:
            ax.scatter([index], [self.extreme_top], marker='*',
                       lw=0.5)

def percentile_box_plot(ax, data, indexer=None, box_top=75,
                        box_bottom=25,whisker_top=99,whisker_bottom=1):
    if indexer is None:
        indexed_data = zip(range(1,len(data)+1), data)
    else:
        indexed_data = [(indexer(datum), datum) for datum in data]
    def get_whisk(vector, w):
        if w is None:
            return None
        return scoreatpercentile(vector, w)

    for index, x in indexed_data:
        bp = boxplotter(scoreatpercentile(x, 50),
                        scoreatpercentile(x, box_top),
                        scoreatpercentile(x, box_bottom),
                        get_whisk(x, whisker_top),
                        get_whisk(x, whisker_bottom),
                        scoreatpercentile(x, 100))
        bp.draw_on(ax, index)


def worst_case_approx(setups, trainlength, plength):
  base_worst = 4.0 * 3
  #base_worst = 0.566
  #packet_time = (plength + 18.0)  * 8.0 / 10.0 / 1000.0
  packet_time = plength * 8.0 / 10.0 / 1000.0
  tmp = [x * (packet_time * trainlength) for x in setups]
  worst = [x + base_worst for x in tmp]
  for i in range(len(worst)):
    print "WORST CASE %d: %f" % (setups[i], worst[i])
  return worst

######################################
if len(sys.argv) < 2:
  print "usage: plot_switch_experiment.py <input dir1> <input1 label> " \
        "<input dir2> <input2 label> ... <output file>"
  sys.exit(1)

paper_mode = True

if paper_mode:
  set_paper_rcs()

# arg processing
if (len(sys.argv) - 1) % 2 == 1:
  # odd number of args, have output name
  outname = sys.argv[-1]
  print "Output name specified: %s" % (outname)
else:
  print "Please specify an output name!"
  sys.exit(1)

inputdirs = []
labels = []
for i in range(1, len(sys.argv)-1, 2):
  inputdirs.append(sys.argv[i])
  labels.append(sys.argv[i+1])

# parsing
data = []
negs_ignored = 0
for indir in inputdirs:
  ds = []
  for line in open(indir).readlines():
  #for line in open(indir).readlines():
    if line.strip() == "":
      continue
    val = float(line.strip()) / 1000.0
    if val > 0:
      ds.append(val)
    else:
      negs_ignored += 1
  data.append(ds)

print "Ignored %d negative latency values!" % (negs_ignored)

# plotting
fig = plt.figure(figsize=(3.33,2.22))
#plt.rc("font", size=7.0)
fig, ax = plt.subplots(figsize=(3.33,2.22))
pos = np.array(range(len(data)))+1
#bp = percentile_box_plot(ax, data)
plt.plot(pos, [np.mean(x) for x in data], marker='+', label='average',
         lw=1.0, color='g')
plt.plot(pos, [np.percentile(x, 99) for x in data], marker='v',
         label='99\\textsuperscript{th}\%ile',
         lw=1.0, color='y', mfc='none', mec='y', mew=1.0)
plt.scatter(pos, [max(x) for x in data], marker='x',
            label='100\\textsuperscript{th}\%ile',
            lw=1.0, color='r')

# worst-case analytical approximation
#plt.plot(range(1, len(data)+1),
#         worst_case_approx(range(0, len(data)), train_length, pkt_size),
#         ':', color='r', label="modelled worst case", lw=1.0)
worst_case_approximation = worst_case_approx([10], train_length, pkt_size)[0]
wc_line = plt.axhline(worst_case_approximation, ls=':', color='r', lw=1.0)
#plt.axvline(worst_case_approx([10], train_length, pkt_size)[0] - 8, ls='--',
#            color='k', lw=1.0, label="optimal network epoch")

first_legend = plt.legend(loc='upper left', frameon=False, handletextpad=0.1,
                          borderaxespad=0.05)
plt.gca().add_artist(first_legend)
plt.legend([wc_line], ["latency bound"], frameon=False, loc='upper center',
           borderaxespad=0.05, handletextpad=0.1)

ax.set_xlabel('Throughput factor $f$')
ax.set_ylabel('End-to-end latency [$\mu$s]')
plt.ylim(0, 30.0)
plt.yticks(range(0, 31, 5), [str(x) for x in range(0, 31, 5)])
plt.xlim(0, len(inputdirs) + 1)
plt.xticks(range(pos[0], pos[-1] + 1, len(pos) / 5),
           [round(worst_case_approximation / float(labels[i-1]), 1)
            for i in range(pos[0], pos[-1] + 1, len(pos) / 5)])

plt.axvspan(0, 5, facecolor='0.8', alpha=0.5, zorder=0, lw=0.0)
plt.axvspan(20.5, 23, facecolor='0.8', alpha=0.5, zorder=0, lw=0.0)
plt.text(2, 31, "\\textbf{A}", fontsize=12)
plt.text(13, 31, "\\textbf{B}", fontsize=12)
plt.text(21.3, 31, "\\textbf{C}", fontsize=12)

#plt.setp(bp['whiskers'], color='k',  linestyle='-' )
#plt.setp(bp['fliers'], markersize=3.0)
plt.savefig(outname, format="pdf", bbox_inches='tight', pad_inches=0.01)
