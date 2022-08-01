#!/bin/bash
#
# JournalList.net combine trust.txf files from sites with common domain shell script.
#
# Name - combine.sh
# Synopsis - combine.sh DOMAIN | DIRNAME
#   DOMAIN - the common domain name
#   DIRNAME - directory containing results of sitescrape.py for a list of URLs
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#-------------------------------------
#
# Check if the argument is a directory, get list of domains with subdirectories from the output.csv file, otherwise arument is the domain
#
if [ -d $1 ]
then
    awk -F "," '{ print $2 }' $1/$1-output.csv | sed -e "s/http:\/\///" -e "s/https:\/\///" -e "s/\/$//" | grep "/" | sed -e "s/\/.*$//" -e "s/^/$1\//" | sort | uniq > domains.tmp
else
    echo $1 > domains.tmp
fi
DOMAINS=$(cat domains.tmp)
echo $DOMAINS
#
for DOMAIN in $DOMAINS
do
    echo "Processing: $DOMAIN"
    #
    # Check if domain trust.txt file exists, if so add it to the list of files. Extract the name and copyright
    #
    if [ -f "$DOMAIN-trust.txt" ]
    then
        FILES="$DOMAIN-trust.txt $DOMAIN-*-trust.txt"
    else
        FILES="$DOMAIN-*-trust.txt"
    fi
    #
    # Extract the name and copyright
    #
    cat $FILES | grep "trust.txt file" | sed -e "s/ trust.txt file//" | head -n 1 > name.tmp
    NAME=$(< name.tmp)
    if [[ "$NAME" != "#"* ]]
    then
        NAME="# <Organization Name Goes Here>"
    fi
    grep -h -e "©" -e "opyright" $FILES | sort | uniq | head -n 1 > copyright.tmp
    #
    # Get all unique attribute entries
    #
    grep -h "belongto=" $FILES | sort | uniq > belongto.tmp
    grep -h "contact=" $FILES | sort | uniq > contact.tmp
    grep -h "control=" $FILES | sort | uniq > control.tmp
    grep -h "controlledby=" $FILES | sort | uniq > controlledby.tmp
    grep -h "customer=" $FILES | sort | uniq > customer.tmp
    grep -h "member=" $FILES | sort | uniq > member.tmp
    grep -h "social=" $FILES | sort | uniq > social.tmp
    grep -h "vendor=" $FILES | sort | uniq > vendor.tmp
    grep -h -e "©" -e "opyright" $FILES | sort | uniq > copyright.tmp
    #
    # Start with header
    #
    echo "$NAME trust.txt file" > $DOMAIN-trust.txt
    echo "#" >> $DOMAIN-trust.txt
    echo "# For more information on trust.txt see:" >> $DOMAIN-trust.txt
    echo "# 1. https://journallist.net - Home of the trust.txt specification" >> $DOMAIN-trust.txt
    echo "# 2. https://datatracker.ietf.org/doc/html/rfc8615 - IETF RFC 8615 - Well-Known Uniform Resource Identifiers (URIs)" >> $DOMAIN-trust.txt
    echo "# 3. https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml - IANA's list of registered Well-Known URIs" >> $DOMAIN-trust.txt
    #
    # Add control= entries if they exist
    #
    if [ -s control.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME controls the following organizations" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat control.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add controlledby= entries if they exist
    #
    if [ -s controlledby.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME is controlled by the following organization" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat controlledby.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add member= entries if they exist
    #
    if [ -s member.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME has the following organizations as members" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat member.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add belongto= entries if they exist
    #
    echo "#" >> $DOMAIN-trust.txt
    echo "$NAME belongs to the following organizations" >> $DOMAIN-trust.txt
    echo "#" >> $DOMAIN-trust.txt
    if [ -s belongto.tmp ]
    then
        cat belongto.tmp >> $DOMAIN-trust.txt
    else
        echo "# belongto=" >> $DOMAIN-trust.txt
    fi
    #
    # Add social= entries if they exist
    #
    if [ -s social.tmp ]
    echo "#" >> $DOMAIN-trust.txt
    echo "$NAME social networks" >> $DOMAIN-trust.txt
    echo "#" >> $DOMAIN-trust.txt
    then
        cat social.tmp >> $DOMAIN-trust.txt
    else
        echo "# social=" >> $DOMAIN-trust.txt
    fi
    #
    # Add vendor= entries if they exist
    #
    if [ -s vendor.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME vendors" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat vendor.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add customer= entries if they exist
    #
    if [ -s customer.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME customers" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat customer.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add contact= entries if they exist
    #
    if [ -s contact.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        echo "$NAME contact information" >> $DOMAIN-trust.txt
        echo "#" >> $DOMAIN-trust.txt
        cat contact.tmp >> $DOMAIN-trust.txt
    fi
    #
    # Add copyright if it exists
    #
    if [ -s copyright.tmp ]
    then
        echo "#" >> $DOMAIN-trust.txt
        head -n 1 copyright.tmp >> $DOMAIN-trust.txt
    fi
done
rm domains.tmp name.tmp belongto.tmp contact.tmp control.tmp controlledby.tmp customer.tmp member.tmp social.tmp vendor.tmp copyright.tmp