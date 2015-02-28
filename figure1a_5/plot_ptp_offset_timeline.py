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

if len(sys.argv) < 2:
  print "usage: plot_ptp_offset_timeline.py <input file 1> <label 1> ... " \
      "<input file n> <label n> [output file]"

paper_mode = True

if (len(sys.argv) - 1) % 2 != 0:
  outname = sys.argv[-1]
  del sys.argv[-1]
else:
  outname = "ptp_timeline"

fnames = []
labels = []
for i in range(0, len(sys.argv) - 1, 2):
  print "Adding file:%s" % (sys.argv[1 + i])
  fnames.append(sys.argv[1 + i])
  print "Adding lable:%s" % (sys.argv[2 + i])
  labels.append(sys.argv[2 + i])

if paper_mode:
  fig = plt.figure(figsize=(2.33,1.55))
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

#fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()

colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', '0.5']

i = 0
minmax = -1
for f in fnames:
  # initial info
  print "Analyzing %s:" % (f)

  # parsing
  j = 0
  values = []
  for line in open(f).readlines():
    fields = [x.strip() for x in line.split(',')]
    if len(fields) < 8 or fields[0] == 'timestamp':
      continue
    offset = float(fields[4]) * 1000.0 * 1000.0
    values.append(offset)
    j += 1

  if minmax == -1:
    minmax = j
  else:
    minmax = min(minmax, j)

  # info output
  print "--------------------------------------"
  print "%s (%s)" % (labels[i], f)
  print "--------------------------------------"
  print "%d total samples" % (j)
  print "--------------------------------------"

  # plotting
#  if paper_mode:
#    plt.rc("font", size=8.0)
  if paper_mode:
    plt.plot(values, label=labels[i],
           color=paper_colors[i % len(paper_colors)], lw=1.0)
  else:
    plt.plot(values, label=labels[i], color=colors[i % len(colors)], lw=1.0)

#  if i == 0:
#    ax1.plot(values, label=labels[i], color=colors[i % len(colors)])
#  else:
#    ax2.plot(values, label=labels[i], color=colors[i % len(colors)])
  i += 1

#plt.xticks(rotation=45)
#plt.yscale("log")
plt.xticks(range(0, 601, 100), [str(x) for x in range(0, 601, 100)])
plt.yticks(range(-400, 601, 200), [str(x) for x in range(-400, 601, 200)])
plt.xlim(0, minmax + 1)
plt.ylim(-500, 750)
plt.ylabel("Clock offset [$\mu$s]")
#ax2.set_ylim(-15, 15)
#ax1.set_ylabel("Clock offset (isolated) [ms]", color=colors[0])
#for tl in ax1.get_yticklabels():
#  tl.set_color(colors[0])
#ax2.set_ylabel("Clock offset (+ BG traffic) [ms]", color=colors[1])
#for tl in ax2.get_yticklabels():
#  tl.set_color(colors[1])
plt.xlabel("Time since start [sec]")
#print n
#print bins
plt.legend(loc=4, frameon=False, labelspacing=0.2, borderaxespad=0.2)

plt.axhline(0, ls=':', color='k')

plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches="tight")
