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
