#! /bin/bash


files=`ls ping* | grep -v "lats" | grep -v "hist"`


for file in $files
do
    cat $file | grep "time=" | cut -d"=" -f 4 | cut -d" " -f 1 > $file.lats
    echo "### " $file " ###"
    ./do_hist.py $file.lats 25
    mv hist_out.ssv $file.hist 
    echo
    echo
done
