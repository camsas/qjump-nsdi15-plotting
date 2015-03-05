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

if len(sys.argv) < 3:
  print("usage: plot_ns2_flow_completion.py <input file> " \
        "<plot_type: mean|99th> <workload: search|learning> " \
        "<region: 1|2|3> <label> ... <label> <output file>")
  sys.exit(1)
"""python plot_ns2_flow_completion.py baseline_largeinitcwnd_log.tr 0 tcp dctcp pdq pfabric ideal qj output.pdf"""

paper_mode = True

if paper_mode:
  fig = plt.figure(figsize=(1.9,1.264))
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

#rc('figure.subplot', left=0.16, top=0.80, bottom=0.18, right=0.84)



colours = ['b', 'r', 'g', 'm', 'c', 'y']

input_file = open(sys.argv[1], 'r')
plot_type = sys.argv[2]
plot_workload = sys.argv[3]
plot_region = int(sys.argv[4])
plot_labels = []
for i in range(5, len(sys.argv) - 1):
    plot_labels.append(sys.argv[i])

outname = sys.argv[-1]

labels = []
nrm_fct_99 = [[]]
nrm_fct_mean = [[]]
cur_label = None
prev_label = None
for line in input_file:
  m = re.match("([a-zA-Z0-9]+)\.([a-zA-Z]+)\.([0-9]\.[0-9])\.?([a-zA-Z0-9]*)\.tr " \
               "region([0-9]): 99% ([0-9\.]+) mean ([0-9\.]+).*", line)
  if m:
    fields = [x.strip() for x in line.split()]
    cur_label = m.group(1)
    cur_label += m.group(4)
    cur_workload = m.group(2)
    if cur_workload != plot_workload:
      continue
    region = int(m.group(5))
    if region != plot_region:
      continue
    if not cur_label in plot_labels:
      continue

    if not prev_label:
      labels.append(cur_label)
      prev_label = cur_label
    if cur_label != prev_label:
      labels.append(cur_label)
      nrm_fct_99.append([])
      nrm_fct_mean.append([])
      prev_label = cur_label
    cur_load = m.group(3)
    percentile99 = float(m.group(6))
    mean = float(m.group(7))
    nrm_fct_99[-1].append(percentile99)
    nrm_fct_mean[-1].append(mean)

input_file.close()

if plot_type == '99th':
  print "%s: REGION %d -- 99th PERCENTILE:" % (outname, plot_region)
  print nrm_fct_99
elif plot_type == 'mean':
  print "%s: REGION %d -- MEAN:" % (outname, plot_region)
  print nrm_fct_mean

x_labels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
num_label = 0
markers = {'baseline':'o', 'dctcp':'+', 'pdq':'v', 'pfabric':'x', 'ideal':'s',
           'qj':'D', }
labels_to_names = {'baseline':'TCP', 'dctcp':'DCTCP', 'pdq':'PDQ',
                   'pfabric':'pFabric', 'ideal':'Ideal', 'qj':'QJump'}
#markers = ['o', 'v', '^', '+', 'x', 'D']

if plot_type == 'mean':
  for i in range(0, len(labels)):
    plt.plot(x_labels, nrm_fct_mean[i], label=labels_to_names[labels[i]],
             color=colours[i], lw=1.0, marker=markers[labels[i]], mew=1.0, mfc='none',
             mec=colours[i], ms=4)
elif plot_type == '99th':
  for i in range(0, len(labels)):
    plt.plot(x_labels, nrm_fct_99[i], label=labels_to_names[labels[i]],
             color=colours[i], lw=1.0, marker=markers[labels[i]], mew=1.0, mfc='none',
             mec=colours[i], ms=4)
else:
  print "Unknown plot type specified!"
  sys.exit(1)

#plt.ylim(1, 10)
plt.xlim(0.1, 0.8)
#ax1.set_yticks([0, 2, 4, 6, 8, 10])
#ax1.set_yticklabels(['0', '2', '4', '6', '8', '10'])
plt.yscale('log')
plt.ylim(1, 35)
plt.yticks([1, 2, 5, 10, 20], ['1', '2', '5', '10', '20'])
plt.xticks([0.2, 0.4, 0.6, 0.8], ['0.2', '0.4', '0.6', '0.8'])
plt.xlabel("Load")
plt.ylabel("Normalized FCT [$\log_{10}$]")
#labs = [l.get_label() for l in lns]
#ax1.legend(lns, labs, bbox_to_anchor=(-0.2, 1.02, 1.2, .102), loc=3,
#           ncol=3, mode="expand", frameon=True, borderaxespad=0.,
#           handletextpad=0.2)
#leg = ax1.get_legend()
#frame = leg.get_frame()
#frame.set_alpha(0.0)
if plot_region == 1 and plot_type == 'mean':
  plt.legend(ncol=2, frameon=False, loc=2, borderaxespad=0.1,
           handletextpad=0.2, columnspacing=0.4)
#plt.figtext(0.01, 0.82, "Latency", rotation='90')
plt.axhline(1, ls=':', color='k')
plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches='tight',
            pad_inches=0.04)
