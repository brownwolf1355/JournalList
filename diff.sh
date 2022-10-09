#!/bin/bash
#
# JournalList.net diff shell script.
#
# Name - cron.sh
# Synopsis - diff.sh DIRNAME1 DIRNAME2
#   DIRNAME1 - the first webcrawl directory
#   DIRNAME1 - the second webcrawl directory
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#-------------------------------------
#
DIRNAME1=$1
DIRNAME2=$2
#
echo ""
echo "Ecosystem Associations"
diff $DIRNAME1/$DIRNAME1-associations.csv $DIRNAME2/$DIRNAME2-associations.csv > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
echo ""
echo "Ecosystem Publishers"
diff $DIRNAME1/$DIRNAME1-publishers.csv $DIRNAME2/$DIRNAME2-publishers.csv > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
echo ""
echo "Ecosystem Vendors"
diff $DIRNAME1/$DIRNAME1-vendors.csv $DIRNAME2/$DIRNAME2-vendors.csv > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
echo ""
echo "JournalList Members"
diff $DIRNAME1/www.journallist.net-trust.txt $DIRNAME2/www.journallist.net-trust.txt > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
echo ""
echo "trust.txt files"
awk -F "," '{ print $1 }' $DIRNAME1/$DIRNAME1.csv | sort | uniq > temp1
awk -F "," '{ print $1 }' $DIRNAME2/$DIRNAME2.csv | sort | uniq > temp2
diff temp1 temp2 > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
echo ""
echo "Well-known.dev resources"
sed "s/[^,]*,\([^,]*\).*/\1/" $DIRNAME1/$DIRNAME1-resources.csv | sort > temp1
sed "s/[^,]*,\([^,]*\).*/\1/" $DIRNAME2/$DIRNAME2-resources.csv | sort > temp2
diff temp1 temp2 > temp
echo "Removed:"
grep "< " temp
echo "Added:"
grep "> " temp
rm temp temp1 temp2
echo ""
echo "Domains with trust.txt files found by well-known.dev"
grep -A 1000 "BEGIN: processing well-known.dev resource list" $DIRNAME2/$DIRNAME2-log.txt | grep "Fetching" | sed -e "s/[^ ]* \([^ ]*\).*/\1/" -e "s/https:\/\/www.//" -e "s/\/trust.txt//"
