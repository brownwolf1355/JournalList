#!/bin/bash
#
# JournalList.net cron shell script.
# 
# Name - cron.sh
# Synopsis - cron.sh [DIRNAME]
#   DIRNAME - optional, the directory in which to place results. Default DIRNAME is "Webcrawl-YYYY-MM-DD".
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#-------------------------------------
date
#
# Set DIRNAME
#
if [ $# == 1 ]
then
    DIRNAME=$1
else
    DIRNAME=( $(date "+Webcrawl-%Y-%m-%d") )
fi
#
# If the directory doesn't already exist. Run the python webcrawler.
#
if [ ! -d $DIRNAME ]
then
    #
    # Generage a resources.csv from all of the historic resources.csv file (downloaded from https://well-known.dev/?q=resource%3Atrust.txt#results) 
    # and copy it to the Webcrawl directory to preserve the results for that day.
    #
    echo "rank,domain,resource,status,scanned,simhash" > temp.csv
    cat resources.csv Webcrawl-*/Webcrawl-*-resources.csv | grep -v "rank,domain,resource,status," | sed -e "s/^[0-9]*,/,/" -e "s/,202.*$/,,/" | sort | uniq >> temp.csv
    mv temp.csv resources.csv
    #
    # Run the webcrawler
    #
    python3.10 webcrawler.py
    #
    # Save resources.csv
    #
    mv resources.csv $DIRNAME/$DIRNAME-resources.csv
fi
#
# Remove duplicate entries. First remove header line, then pipe to sort and uniq, next reinsert header line, and follow it with the sorted-unique list of entries.
#
tail -n +2 $DIRNAME/$DIRNAME.csv | sort | uniq > $DIRNAME/temp
echo "srcurl,attr,refurl" > $DIRNAME/$DIRNAME.csv
cat $DIRNAME/temp >> $DIRNAME/$DIRNAME.csv
rm $DIRNAME/temp
#
# Process the results of the webcrawler to generate the symmetric links, association, publisher, and vendor .csv files.
#
echo ".import $DIRNAME/$DIRNAME.csv trust_txt" > temp.sql
echo ".import $DIRNAME/$DIRNAME-err.csv http_errors" >> temp.sql
echo ".read symmetric.sql" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-symmetric.csv" >> temp.sql
echo "select distinct * from symmetric_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-asymmetric.csv" >> temp.sql
echo "select distinct * from asymmetric_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-associations.csv" >> temp.sql
echo "select distinct * from associations_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-publishers.csv" >> temp.sql
echo "select distinct * from publishers_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-vendors.csv" >> temp.sql
echo "select distinct * from vendors_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-controlled.csv" >> temp.sql
echo "select distinct * from controlled_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-control_dups.csv" >> temp.sql
echo "select distinct * from control_dups;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-controlledby_dups.csv" >> temp.sql
echo "select distinct * from controlledby_dups;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-missctrlby.csv" >> temp.sql
echo "select * from missctrlby_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-stats.csv" >> temp.sql
echo "select * from stats;" >> temp.sql
echo ".quit" >> temp.sql
#
cat temp.sql | sqlite3 -init init.sql 2> /dev/null
rm temp.sql
#
# Process the symmetric.csv file to generate the .graphml files.
#
python3.10 graphml.py $DIRNAME
#
# Generate the JSON files for ArangoDB graph database
#
bash genjson.sh $DIRNAME
#
# Output the start time and end time
#
echo "JournalList trust.txt webcrawl"
head -n 1 $DIRNAME/$DIRNAME-log.txt
tail -n 1 $DIRNAME/$DIRNAME-log.txt
