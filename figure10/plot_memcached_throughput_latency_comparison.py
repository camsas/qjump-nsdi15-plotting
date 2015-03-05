
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

import os, sys, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from utils import *

if len(sys.argv) < 2:
  print "usage: plot_throughput_latency_comparison.py <input file 1> " \
      "<label 1> ... <input file n> <label n> [output file]"

paper_mode = True
subset_mode = False

if (len(sys.argv) - 1) % 2 != 0:
  outname = sys.argv[-1]
else:
  outname = "memcached_throughput_latency"

fnames = []
labels = []
for i in range(0, len(sys.argv) - 1, 2):
  fnames.append(sys.argv[1 + i])
  labels.append(sys.argv[2 + i])

if paper_mode:
  fig = plt.figure(figsize=(3.33,2.22))
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

rc('figure.subplot', left=0.16, top=0.80, bottom=0.18, right=0.84)

fig, ax1 = plt.subplots(figsize=(2.72, 1.81))
ax2 = ax1.twinx()

colours = ['b', 'r', 'y', 'm', 'c', 'y']

i = 0
throughput_values = []
latency_values_avg = []
latency_values_med = []
latency_values_99th = []
latency_values_min = []
latency_values_max = []
for f in fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  lat_values = []
  req_count = 0
  start_time = -1
  end_time = -1
  for line in open(f).readlines():
    fields = [x.strip() for x in line.split(' ')]
    if len(fields) != 4 or fields[0] != 'TOTAL':
      continue
    if start_time == -1:
      start_time = int(fields[2])
    if end_time == -1:
      end_time = int(fields[2])
    start_time = min(start_time, int(fields[2]))
    end_time = max(end_time, int(fields[2]))
    lat = float(fields[3])
    lat_values.append(lat)
    req_count += 1

  # info output
  runtime_sec = float(end_time - start_time) / 1000.0 / 1000.0 / 1000.0
  print end_time
  print start_time
  throughput = float(req_count) / runtime_sec
  print "--------------------------------------"
  print "%s (%s)" % (labels[i], f)
  print "--------------------------------------"
  print "%d total samples" % (req_count)
  print "%ds runtime" % (runtime_sec)
  print "--------------------------------------"
  print "THROUGHPUT: %f req/s" % throughput
  print "LATENCY AVG: %fus" % np.mean(lat_values)
  print "LATENCY MEDIAN: %fus" % np.median(lat_values)
  print "LATENCY 99th PERC: %fus" % np.percentile(lat_values, 99)

  throughput_values.append(throughput / 1000.0)
  latency_values_avg.append(np.mean(lat_values))
  latency_values_med.append(np.median(lat_values))
  latency_values_min.append(min(lat_values))
  latency_values_99th.append(np.percentile(lat_values, 99))
  latency_values_max.append(max(lat_values))

  print "\n"

  i += 1

# plotting
#    plt.rc("font", size=8.0)
x_labels = [float(x) * 128.0 * 8.0 / 100.0 / 1000.0 for x in labels]

ax1 = plt.axes([0., 0., 1., 0.5])
#lns += ax1.plot(x_labels, latency_values_avg, label="avg latency",
#                color='b', lw=1.0, marker='+', mew=1.0)
lns = ax1.plot(x_labels, latency_values_max, label="Max.~latency",
               color=colours[1], lw=1.0, marker='x', mew=1.0, mfc='none',
               mec=colours[1], ms=5)
lns += ax1.plot(x_labels, latency_values_99th, label="99\%ile latency",
                color=colours[2], lw=1.0, marker='v', mew=1.0, mfc='none',
                mec=colours[2], ms=5)
#lns += ax1.plot(x_labels, latency_values_med, label="50\% lat.",
#                color=colours[3], lw=1.0, marker='^', mew=1.0, mfc='none',
#                mec=colours[3], ms=4)
#lns += ax1.plot(x_labels, latency_values_min, label="Min.~lat.",
#                color=colours[4], lw=1.0, marker='+', mew=1.0, mfc='none',
#                mec=colours[4], ms=4)

ax2 = plt.axes([0., 0.5, 1., 0.5])
lns += ax2.plot(x_labels, throughput_values, label="Throughput",
                color=colours[0], lw=1.0, marker='s', mew=1.0, mfc='none',
                mec=colours[0], ms=5)


#plt.xticks(rotation=45)
#plt.yscale("log")
ax2.set_xlim(0, 10.1)
#plt.ylim(-0.5, 0.75)
#plt.ylabel("Clock offset [ms]")
#ax2.set_ylim(-15, 15)
# right hand axis
ax2.set_ylabel("Throughput [kreq/s]")
ax2.set_yticks([0, 50, 100, 150, 200])
ax2.set_yticklabels(['0', '50', '100', '150', '200'])
#for tl in ax2.get_yticklabels():
#  tl.set_color(colours[0])
# left hand axis
#ax1.set_ylabel("Latency")
if subset_mode:
  ax1.set_ylim(10, 1000)
  ax1.set_yticks([10, 100, 1000])
  ax1.set_yticklabels(['10$\mu$s', '100$\mu$s', '1ms'])
else:
  ax1.set_yscale('log')
  ax1.set_yticks([10, 100, 1000, 10000, 100000, 1000000, 10000000])
  ax1.set_yticklabels(['10$\mu$s', '100$\mu$s', '1ms', '10ms', '100ms',
                       '1s', ''])
  ax1.set_ylim(ymax=10000000)
  ax1.set_ylabel('Latency [$\log_{10}$]')
#for tl in ax1.get_yticklabels():
#  tl.set_color(colours[1])
ax1.set_xlim(0, 10.1)
ax1.set_xlabel("Rate limit [Gb/s]")
ax1.set_xticks([0, 2, 4, 6, 8, 10])
ax1.set_xticklabels(['0', '2', '4', '6', '8', '10'])

ax2.set_xticks([0, 2, 4, 6, 8, 10])
ax2.set_xticklabels(['', '', '', '', '', ''])
#print n
#print bins
#ax2.legend(loc=1, frameon=False)
#ax1.legend(loc=7, frameon=False)
ax1.legend(loc='upper right', frameon=False)
ax2.legend(loc='lower right', frameon=False)
#labs = [l.get_label() for l in lns]
#ax1.legend(lns, labs, bbox_to_anchor=(-0.14, 1.02, 1.4, .102), loc=3,
#           ncol=3, mode="expand", frameon=False, borderaxespad=0.)
#ax2.legend(lns, labs, loc="lower right", frameon=False,
#           borderaxespad=0.1)

ax1.axvspan(5.0, 5.5, lw=0, color='0.8')
ax2.axvspan(5.0, 5.5, lw=0, color='0.8')
ax2.annotate('best tradeoff', xy=(0.5, 0.5), xycoords='axes fraction',
             xytext=(20, 0), textcoords='offset points',
             arrowprops=dict(arrowstyle="->"), ha='left')


#ax1.axhline(100, ls=':', color='k')
#ax1.axhline(200, ls=':', color='k')
#ax1.axhline(400, ls=':', color='k')
#ax1.axhline(600, ls=':', color='k')
#ax1.axhline(800, ls=':', color='k')
#ax1.axhline(1000, ls=':', color='k')

#plt.axvspan(2560, 5120, facecolor='0.8', alpha=0.5)
#plt.figtext(0.01, 0.82, "Latency", rotation='90')

plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches='tight',
            pad_inches=0.05)
