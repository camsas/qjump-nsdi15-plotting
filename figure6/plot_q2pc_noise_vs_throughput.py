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
  print "usage: plot_q2pc_noise_vs_throughput.py <input file> "\
      "<setup 1> <label 1> ... <setup n> <label n>"

paper_mode = True

outname = "q2pc_noise_throughput"

input_file = sys.argv[1]

setup_filter = {}
for i in range(2, len(sys.argv), 2):
  setup = sys.argv[i]
  label = sys.argv[i+1]
  print "%s -> %s" % (setup, label)
  setup_filter[setup] = label

print setup_filter

if paper_mode:
  fig = plt.figure(figsize=(3, 2))
  set_paper_rcs()
else:
  fig = plt.figure()
  set_rcs()

#rc('figure.subplot', left=0.16, top=0.80, bottom=0.18, right=0.84)

#fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()

markers = ['x', 'v', 'o', '^', '+']
colours = ['#496ee2', '#8e053b', '#ef9708', 'g', '0', '#eeefff', '0.5', 'c', '0.7']

i = 0
noise_values = {}
throughput_values = {}
latency_values_min = {}
latency_values_med = {}
latency_values_max = {}
# parsing
lat_values = []
first = True
for line in open(input_file).readlines():
  if first:
    first = False
    continue
  fields = [x.strip() for x in line.split(',')]
  print "working on %s" % (fields)
  setup = fields[0]
  noise = int(fields[1])
  throughput = float(fields[5])
  min_lat = float(fields[6])
  med_lat = float(fields[7][:-2])
  max_lat = float(fields[8])

  if not setup in noise_values:
    noise_values[setup] = []
  if not noise in noise_values[setup]:
    noise_values[setup].append(noise)
  if not setup in throughput_values:
    throughput_values[setup] = {}
    latency_values_min[setup] = {}
    latency_values_med[setup] = {}
    latency_values_max[setup] = {}
  append_or_create(throughput_values[setup], noise, throughput)
  append_or_create(latency_values_min[setup], noise, min_lat)
  append_or_create(latency_values_med[setup], noise, med_lat)
  append_or_create(latency_values_max[setup], noise, max_lat)

#print noise_values
#print throughput_values

i = 0
for setup, nvs in noise_values.items():
  print "Analysing %s..." % (setup),
  if not setup in setup_filter:
    print "SKIP"
    continue
  noise_vals = []
  throughput_values_avg = []
  throughput_values_std = []
  for nv in nvs:
    noise_vals.append(nv)
    throughput_values_avg.append(np.mean(throughput_values[setup][nv]))
    throughput_values_std.append(np.std(throughput_values[setup][nv]))

  print noise_vals
  print throughput_values_avg
  lns = plt.errorbar(noise_vals, throughput_values_avg,
                     yerr=throughput_values_std, label=setup_filter[setup],
                     color=colours[i % len(colours)], lw=1.0,
                     marker=markers[i % len(markers)], ms=4,
                     mew=0.5, mec=colours[i % len(colours)],
                     elinewidth=0.5, capsize=1, markevery=2)
  i += 1

#plt.annotate('\\large\\textbf{\\dag}', xy=(0.7, 0.5),  xycoords='axes fraction',
#             textcoords='offset points',
#             color='#496ee2' )

#plt.yscale("log")
plt.ylim(0, 15000)
plt.yticks(range(0, 14001, 2000), [str(x) for x in range(0, 14001, 2000)])
plt.xscale("log", basex=2)
plt.xlim(0.75, 6144)
#plt.xticks([2**x for x in range(1, 14)], [str(2**x) for x in range(1, 14)])
x_label_values = [1, 2, 4, 8, 16, 32, 62, 125, 250, 500, 1000, 2000, 4000]
x_percent_labels = ["%.1f\%%" % (float(x)*1500/1024/1024/(1200*1000/.1/8/1024/1024)*100.0)
                    for x in x_label_values]
plt.xticks(x_label_values,
           [x_percent_labels[i] if i % 2 == 0 else "" for i in range(len(x_label_values))],
            rotation=45, ha='right')


#plt.xlim(0, 10.1)
#plt.ylim(-0.5, 0.75)
#plt.ylabel("Clock offset [ms]")
#ax2.set_ylim(-15, 15)
# right hand axis
plt.ylabel("Throughput [req/s]")
#for tl in ax1.get_yticklabels():
#  tl.set_color(colours[1])
plt.xlabel("Burst size / switch buffer size [$\log_2$]")
plt.legend(loc="lower left", frameon=False)
#print n
#print bins
#ax2.legend(loc=1, frameon=False)
#ax1.legend(loc=7, frameon=False)
#plt.axvspan(2560, 5120, facecolor='0.8', alpha=0.5)

plt.savefig("%s.pdf" % outname, format="pdf", bbox_inches='tight', pad_inches=0.01)
