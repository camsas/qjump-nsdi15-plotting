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

import os, sys, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from utils import *

if len(sys.argv) < 7:
  print "usage: plot_ptp_memcached_hadoop_timeline.py " \
      "<PTP idle input> <memcached idle input> " \
      "<PTP contended/P0 input> <memcached contended/P0 input> " \
      "<PTP contended/P7 input> <memcached contended/P5 input> [output file]"

paper_mode = True

if (len(sys.argv) - 1) % 2 != 0:
  outname = sys.argv[-1]
else:
  outname = "ptp_memcached_hadoop_timeline"

ptp_fnames = [sys.argv[1], sys.argv[3], sys.argv[5] ]
memd_fnames = [sys.argv[2], sys.argv[4], sys.argv[6] ]

if paper_mode:
  fig = plt.figure(figsize=(3.33,3.33))
  plt.subplots_adjust(hspace=0)
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

#fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()

if paper_mode:
  colors = paper_colors
else:
  colors = ['b', 'r', 'g', 'm', 'c', 'y']

i = 0
minmax = -1
ptp_times = []
ptp_values = []
memd_times = []
memd_values = []
for f in ptp_fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  j = 0
  values = []
  times = []
  for line in open(f).readlines():
    # ptpd
    fields = [x.strip() for x in line.split(',')]
    if len(fields) < 8 or fields[0] == 'timestamp':
      continue
    offset = float(fields[4]) * 1000.0 * 1000.0
    times.append(j)
    values.append(offset)
    j += 1

  ptp_times.append(times)
  ptp_values.append(values)

for f in memd_fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  j = 0
  values = []
  times = []
  for line in open(f).readlines():
    # memcached
    fields = [x.strip() for x in line.split(' ')]
    if len(fields) != 2:
      continue
    time = float(fields[0])
    lat = float(fields[1])
    times.append(time)
    values.append(lat)
    j += 1

  memd_times.append(times)
  memd_values.append(values)

# plotting

###############
# IDLE CASE
ax1_1 = plt.subplot(311)
ax1_1.plot(memd_times[0], memd_values[0], label="memcached",
           color=colors[1], lw=1.0)
ax1_1.plot(ptp_times[0], ptp_values[0], label="PTPd",
           color=colors[0], lw=1.0)
ax1_1.set_ylim(-200, 1400)
ax1_1.axhline(0.0, ls=':', color='k')
ax1_1.legend(loc=9, frameon=False, borderaxespad=0.2)
ax1_1.set_xlim(150, 375)
ax1_1.set_xticks([])
ax1_1.set_yticks(range(0, 1401, 400))
ax1_1.set_yticklabels([str(x) for x in range(0, 1401, 400)])
ax1_1.text(160, 1100, "\\textbf{IDLE}")

###############
# CONTENDED CASE
ax2_1 = plt.subplot(312)
ax2_1.plot(memd_times[1], memd_values[1],
           color=colors[1], lw=1.0)
ax2_1.plot(ptp_times[1], ptp_values[1],
           color=colors[0], lw=1.0)
ax2_1.set_ylim(-200, 1400)
ax2_1.axhline(0.0, ls=':', color='k')
ax2_1.legend(loc=9, frameon=False)
ax2_1.set_xlim(150, 375)
ax2_1.set_xticks([])
ax2_1.set_yticks(range(0, 1401, 400))
ax2_1.set_yticklabels([str(x) for x in range(0, 1401, 400)])
ax2_1.text(160, 1100, "\\textbf{CONT.}")

###############
# QJ CASE
ax3_1 = plt.subplot(313)
ax3_1.plot(memd_times[2], memd_values[2],
           color=colors[1], lw=1.0)
ax3_1.plot(ptp_times[2], ptp_values[2],
           color=colors[0], lw=1.0)
ax3_1.set_ylim(-200, 1400)
ax3_1.axhline(0.0, ls=':', color='k')
ax3_1.legend(loc=9, frameon=False)
ax3_1.set_xlim(150, 375)
ax3_1.set_xticks(range(150, 376, 50))
ax3_1.set_xticklabels([str(x) for x in range(150, 376, 50)])
ax3_1.set_yticks(range(0, 1401, 400))
ax3_1.set_yticklabels([str(x) for x in range(0, 1401, 400)])
ax3_1.text(160, 1100, "\\textbf{CONT.~+ QJ}")

#plt.xticks(rotation=45)
#plt.yscale("log")
#plt.xlim(0, minmax + 1)
#plt.ylabel("Latency")
#ax2.set_ylim(-15, 15)
#ax1.set_ylabel("Clock offset (isolated) [ms]", color=colors[0])
#for tl in ax1.get_yticklabels():
#  tl.set_color(colors[0])
#ax2.set_ylabel("Clock offset (+ BG traffic) [ms]", color=colors[1])
#for tl in ax2.get_yticklabels():
#  tl.set_color(colors[1])
plt.xlabel("Time since start [sec]")
plt.figtext(-0.02, 0.8, "Latency (memcached) / Offset (ptpd) [$\mu$s]", rotation=90)
#plt.ylabel("Latency [$\mu$s]")
#print n
#print bins


plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches="tight")
