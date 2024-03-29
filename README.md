# JournalList

This is a repository for code developed for JournalList.net.

It contains the following files:

- cron.sh - a bash shell script that runs the python webcrawler, processes the results through sqlite, and generates graphml files of the results.
- webcrawler.py - a python script that recursively crawls trust.txt files to capture the state of the trust.txt ecosystem. It captures a copy of 
  all of the trust.txt files it finds and generates a .csv file of the contents of all of them.
- init.sql - the initialization sqlite script that creates the intermediate tables used in the following sql script.
- symmetric - a sql script that generates .csv files containing the symmetric links in the trust.txt ecosystem and list of associations, publishers,
  and vendors discovered.
- graphml.py - a python script that generates three graphml files containing the symmetric links, the assymetric links, and the full ecosystem including
  both the symmetric and asymmetric links.
- qa_trust_txt.py - a python script that parses a trust.txt file and lists any errors it contains.
- genjson.sh - a shell script that generates two JSON files suitable for import into the ArangoDB graph database for social network analysis
- genlink.awk - an awk script that generates the link.json file for import into ArangoDB
- genurl.awk - an awk script that generates the url.json file for import into ArangoDB
- scrapesite.py - a python script that scrapes websites to scan one or more sites and find all social, contact, and vendor links, as well as control links and copyright.
- tpa.awk - an example awk script that process an output.csv file from scrapesite to generate multiple trust.txt files.

Copyright (c) 2021 Brown Wolf Consulting LLC

License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
