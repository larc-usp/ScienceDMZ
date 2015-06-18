#!/usr/bin/env bash

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
    killall -9 python
    mn -c
    exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`
outdir=results-$exptid

# Note: you need to make sure you report the results
# for the correct port!
# In this example, we are assuming that each
# client is connected to port 2 on its switch.

for n in 1; do
    size=25
    bw=100

    python measure.py \
        --dir $outdir \
	--bw $bw \
	--time 5 \
	--size $size 
#	--cli

    echo "*** Creating iperf plots"
    python util/plot_rate.py \
	--main "iperf TX Rates ($bw Mbps)" \
	--maxy $bw \
        -f $outdir/bwm-iperf.txt \
        -o $outdir/rate-iperf.png

<<COMMENT
    python util/plot_tcpprobe.py \
        -f $outdir/tcp_probe.txt \
        -o $outdir/cwnd.png
COMMENT

    echo "*** Creating file transer plots"
    python util/plot_rate.py \
	--main "scp TX Rates ($size MB at $bw Mbps)" \
	--maxy $bw \
        -f $outdir/bwm-tx.txt \
        -o $outdir/rate-tx.png
done

echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $outdir"
