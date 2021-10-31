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
    python3.10 webcrawler.py
fi
#
# Process the results of the webcrawler to generate the symmetric links, association, publisher, and vendor .csv files.
#
echo ".import $DIRNAME/$DIRNAME.csv trust_txt" > temp.sql
echo ".import $DIRNAME/$DIRNAME-err.csv http_errors" >> temp.sql
echo ".read symmetric.sql" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-symmetric.csv" >> temp.sql
echo "select * from symmetric_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-asymmetric.csv" >> temp.sql
echo "select * from asymmetric_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-associations.csv" >> temp.sql
echo "select * from associations_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-publishers.csv" >> temp.sql
echo "select * from publishers_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-vendors.csv" >> temp.sql
echo "select * from vendors_list;" >> temp.sql
echo ".output $DIRNAME/$DIRNAME-controlled.csv" >> temp.sql
echo "select * from controlled_list;" >> temp.sql
echo ".quit" >> temp.sql
#
cat temp.sql | sqlite3 -init init.sql
rm temp.sql
#
# Process the symmetric.csv file to generate the .graphml files.
#
python3.10 graphml.py $DIRNAME
