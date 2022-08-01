#!/bin/bash
#
# JournalList.net generate trust.txf file for site(s) that control multiple domains.
#
# Name - control.sh
# Synopsis - combine.sh DIRNAME
#   DIRNAME - directory containing results of sitescrape.py for a list of URLs
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#-------------------------------------
#
LENHEAD=6
#
# If the argument is not a directory, print error
#
DIR=$1
if [ -d $DIR ]
then
    #
    # Generate the set of "control=" relationships and list of controlling entities from the output.csv file
    #
    awk -F "," '{ if ($6 != "" && $6 != "Controlledby") printf "%s,%s\n",$6,$2 }' "$DIR/$DIR-output.csv" | sort | uniq > controlledby.tmp
    awk -F "," '{ print $1 }' controlledby.tmp | sort | uniq > controls.tmp
    CONTROLS=$(cat controls.tmp)
    # echo $CONTROLS
    #
    # For each controlling entity
    #
    for CONTROL in $CONTROLS
    do
        # echo "Processing: $CONTROL"
        #
        # Generate a trust.txt file for the controlling entity
        #
        WEBCRAWL=( $(ls | grep Webcrawl | tail -n 1) )
        python3.10 sitescrape.py -d $DIR -w $WEBCRAWL $CONTROL
        #
        # Extract the name and copyright
        #
        TRUSTTXT=${CONTROL#*://}
        TRUSTXT=${TRUSTTXT%\/}
        cat "$DIR/$TRUSTXT-trust.txt" | grep "trust.txt file" | sed -e "s/ trust.txt file//" | head -n 1 > name.tmp
        NAME=$(< name.tmp)
        #
        # Start with header
        #
        head -n $LENHEAD "$DIR/$TRUSTXT-trust.txt" > temp-trust.txt
        #
        # Extract existing "control=" entries from trust.txt file and add any found in output.csv file
        #
        grep "control=" "$DIR/$TRUSTXT-trust.txt" > entries.tmp
        LENENT=$(wc -l < entries.tmp)
        grep -h $CONTROL controlledby.tmp | sed -e "s/^.*,/control=/" >> entries.tmp
        #
        # Add control= entries
        #
        echo "#" >> temp-trust.txt
        echo "$NAME controls the following organizations" >> temp-trust.txt
        echo "#" >> temp-trust.txt
        cat entries.tmp | sort | uniq >> temp-trust.txt
        #
        # Add remainder of the trust.txt file
        #
        LEN=$(wc -l < "$DIR/$TRUSTXT-trust.txt")
        if [ $LENENT == 0 ]
        then
            TAIL=$(($LEN-$LENHEAD-$LENENT))
        else
            TAIL=$(($LEN-$LENHEAD-$LENENT-3))
        fi
        tail -n $TAIL "$DIR/$TRUSTXT-trust.txt" >> temp-trust.txt
        mv temp-trust.txt "$DIR/$TRUSTXT-trust.txt"
    done
    rm name.tmp controls.tmp controlledby.tmp entries.tmp
else
    echo "$DIR not a directory"
fi