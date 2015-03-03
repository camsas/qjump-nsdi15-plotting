
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


import re, sys
import matplotlib
matplotlib.use('Agg')
from utils import *
import matplotlib.pyplot as plt
import numpy as np

def usage():
  print "plot_pf_ecn_dctcp_barchart.py <input file> <cat1> <label1> " \
        "<cat2> <label2> ... <catN> <labelN> [output file]"
  sys.exit(1)

def on_draw(event):
   bboxes = []
   for label in labels:
       bbox = label.get_window_extent()
       # the figure transform goes from relative coords->pixels and we
       # want the inverse of that
       bboxi = bbox.inverse_transformed(fig.transFigure)
       bboxes.append(bboxi)

   # this is the bbox that bounds all the bboxes, again in relative
   # figure coords
   bbox = mtransforms.Bbox.union(bboxes)
   if fig.subplotpars.left < bbox.width:
       # we need to move it over
       fig.subplots_adjust(left=1.1*bbox.width) # pad a little
       fig.canvas.draw()
   return False

def autolabel(rect, thrval):
  # attach some text labels
  height = rect.get_height()
  if height > thrval:
    plt.text(rect.get_x()+float(rect.get_width())/2.0, thrval-0.05*thrval,
             '%.0f' % float(height),
             ha='center', va='top', rotation='vertical', size='x-small',
             weight='bold', color='k')

def normalize_list_by_value(l, v):
  nl = []
  for e in l:
    nl.append(e / v)
  return nl

def normalize_list_by_list(l1, l2):
  nl = []
  if len(l1) != len(l2):
    print "Tried to normalise list of length %d by list of length %d" \
      % (len(l1), len(l2))
    sys.exit(1)
  for i in range(len(l1)):
    if l1[i] == 0.0 or l2[i] == 0.0:
      nl.append(0.0)
    else:
      nl.append(l1[i] / l2[i])
  return nl

if len(sys.argv) < 2:
  usage()
  sys.exit()

input_file = sys.argv[1]
num_setups = len(sys.argv) - 2
if (len(sys.argv) - 2) % 2 == 1:
  print "Output file name is %s" % (sys.argv[-1])
  output_file = sys.argv[-1]
  num_setups -= 1
else:
  output_file = input_file + ".pdf"

# get benchmarks to include and their labels from command line args
setups = []
setup_labels = []
for i in range(2, num_setups+2, 2):
  setups.append(sys.argv[i])
  setup_labels.append(sys.argv[i+1])
  print "%s -> %s" % (sys.argv[i], sys.argv[i+1])

set_paper_rcs()

raw_had_bars_avg = []
raw_had_bars_std = []
raw_ptpd_bars_avg = []
raw_ptpd_bars_std = []
raw_memd_bars_avg = []
raw_memd_bars_std = []
cur_setup = ""
for line in open(input_file).readlines():
  fields = [x.strip() for x in line.split(",")]
  if len(fields) == 0 or fields[0] == "":
    continue
  cur_setup = fields[0]
  val_hadoop = float(fields[1])
  val_ptp = float(fields[2])
  val_memd = float(fields[3])
  std_hadoop = float(fields[4])
  std_ptp = float(fields[5])
  std_memd = float(fields[6])
  #print fields
  # skip any setups we're not interested in plotting
  if not cur_setup in setups:
    continue
  raw_had_bars_avg.append(val_hadoop)
  raw_had_bars_std.append(std_hadoop)
  raw_ptpd_bars_avg.append(val_ptp)
  raw_ptpd_bars_std.append(std_ptp)
  raw_memd_bars_avg.append(val_memd)
  raw_memd_bars_std.append(std_memd)

# number of setups
num_setups = len(setups)

# Plotting
fig = plt.figure(figsize=(3.1, 2.0))
plt.axes([0.14, 0.23, 0.86, 0.64])

#plt.subplot(221)
#plt.subplots_adjust(wspace=0.5)

offset = 0
bar_locs = np.arange(num_setups)
width = 0.2
print width
#8e053b red  Metis
#496ee2 blue Hadoop
#ef9708 orange Spark
colors = ['#496ee2', '#ef9708', '#8e053b', '0.5', 'g', 'k']
hatches = [ '///', None, '///', None, '///', None, '///', None]

# ---------------------------------------------------------------------------

print raw_had_bars_avg
print raw_ptpd_bars_avg
print raw_memd_bars_avg
normed_had_bars_avg = normalize_list_by_value(raw_had_bars_avg, raw_had_bars_avg[0])
normed_had_bars_std = normalize_list_by_list(raw_had_bars_std, raw_had_bars_avg)
normed_ptpd_bars_avg = normalize_list_by_value(raw_ptpd_bars_avg, raw_ptpd_bars_avg[0])
normed_ptpd_bars_std = normalize_list_by_list(raw_ptpd_bars_std, raw_ptpd_bars_avg)
normed_memd_bars_avg = normalize_list_by_value(raw_memd_bars_avg, raw_memd_bars_avg[0])
normed_memd_bars_std = normalize_list_by_list(raw_memd_bars_std, raw_memd_bars_avg)

maxy = 3.0
labels = []
base_value = 0
rects1 = plt.bar(bar_locs+width*0+0.2, normed_had_bars_avg, width,
                 color=colors[0 % len(colors)], yerr=normed_had_bars_std,
                 ecolor='k', label="Hadoop\nruntime")
rects2 = plt.bar(bar_locs+width*1+0.2, normed_ptpd_bars_avg, width,
                 color=colors[1 % len(colors)], yerr=normed_ptpd_bars_std,
                 ecolor='k', label="PTPd sync.\noffset")
rects3 = plt.bar(bar_locs+width*2+0.2, normed_memd_bars_avg, width,
                 color=colors[2 % len(colors)], yerr=normed_memd_bars_std,
                 ecolor='k', label="memcached\nreq.~latency")
for rect in rects1:
  autolabel(rect, maxy)
for rect in rects2:
  autolabel(rect, maxy)
for rect in rects3:
  autolabel(rect, maxy)
#  labels.append(rect)

plt.axhline(1.0, color='k', ls="-", lw=0.75)

plt.xticks(np.arange(0.5, float(num_setups) + 0.5, 1.0),
           setup_labels, ha='right', rotation=20)
#plt.xlim(0, len())
plt.ylim(0, maxy)
#plt.axhline(base_value, ls='--', color='k', lw=1.0)
plt.yticks([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
           ["0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0"])
plt.ylabel("Normalized RMS app.~metric")
#plt.legend(loc='upper right', frameon=False, borderaxespad=0.01, labelsep=0.01)
leg = plt.legend(loc='upper left', bbox_to_anchor = (0.0, 1.17, 1.0, 0.1),
                 labelspacing=0.2, frameon=False, ncol=3, handletextpad=0.4,
                 columnspacing=0.7)
#leg = plt.legend(labels, systems, loc=7, labelspacing=0.2, ncol=1,
#                 frameon=False)

#plt.show()
plt.savefig(output_file, format="pdf", transparent=True)
