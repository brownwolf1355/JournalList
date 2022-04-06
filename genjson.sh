#!/bin/bash
#
# JournalList.net genjson shell script. Generates urls and links json files from .csv file.
#
# Name - genjson.sh
# Synopsis - gensjon.sh DIRNAME
#   DIRNAME - the webcrawl directory
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#-------------------------------------
#
DIRNAME=$1
#
# Generate json urls
#
sed -e "/srcurl,attr,refurl/d" -e "s/,.*,/\n/" $DIRNAME/$DIRNAME.csv | sort | uniq > temp1
NL1=( $(wc -l temp1) )
awk -v NL=$NL1 -f genurl.awk temp1 > $DIRNAME/$DIRNAME-urls.json
#
# Generate json links
#
sed -e "/srcurl,attr,refurl/d" $DIRNAME/$DIRNAME.csv > temp2
NL2=( $(wc -l temp2) ) 
awk -F "," -v NL1=$NL1 -v NL2=$NL2 -f genlink.awk temp1 temp2 > $DIRNAME/$DIRNAME-links.json
#
rm temp1 temp2
