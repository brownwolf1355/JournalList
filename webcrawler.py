#!/usr/local/bin/python3.10
#
# JournalList.net webcrawler to recursively find all trust.txt files referenced by "member", 
# "belongto", "vendor", "consumer", "control", and "controlledby" entries.
#
# Name - webcrawler.py
# Synopsis - webcrawler.py [ROOT_URL]
#   ROOT_URL - optional, the domain URL (absent "trust.txt") where to begin webcrawl. Default
#   is "https://www.journallist.net/"
#
# Summary - This python script has several outputs:
# 
# 1. It downloads the trust.txt files that exist from all referenced urls with attributes
#    ("member", "belongto", "vendor", "consumer") into a subdirectory Webcrawl-YYYY-MM-DD
#    to preserve a snapshot of them for that day. 
# 2. It generates a Webcrawl-YYYY-MM-DD.csv file capturing all of the URL references in these
#    trust.txt files under three columns (srcurl,attr,refurl):
#     - srcurl is the URL for the trust.txt file
#     - attr is one of the trust.txt attributes, e.g., "member", "belongto", "vendor", "consumer", 
#       "control", "controlledby", "social", "control", "contact", "disclosure"
#     - refurl is the referenced URL associated with the attribute.
# 3. It generates a Webcrawl-YYYY-MM-DD-log.txt file that provides useful debug information.
# 4. It generates a Webcrawl-YYYY-MM-DD-err.csv file that lists all of the urls that generated
#    errors under two columns:
#    - url is the url that generated the error
#    - error is the error status code or "HTML" if the content is an HTML page or "exception"
#      if the request throws and exception.
#
# The webcrawler downloads the trust.txt file for the ROOT_URL, then extracts all "member", 
# "belongto", "vendor", "consumer", "control", and "controlledby" referenced URLs and recursively
# downloads and process each.
# 
# To insure that source urls and referenced urls match it is necessary to normalizes all URLs to 
# be of the form http[s]://www.domain.com/, (e.g., all lowercase, with leading "www." and trailing
#  "/")
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import time
import requests
#
# normalize(url) - Normalize url path to the form "www.domain.com/", (e.g., all lowercase, with
# leading "www." and trailing "/"). Strip the leading "http[s]://" if necessary.
# 
def normalize (url):
    # Stip whitespace, convert to lower case, make sure there is a leading "www." and trailing "/", return protocol and path separately.
    #
    tmpurl = url.strip().lower()
    #
    # Remove leading protocol, if necessary
    #
    if ("http://" in tmpurl):
        tmppath1 = tmpurl[7:len(tmpurl)]
    elif ("https://" in tmpurl):
        tmppath1 = tmpurl[8:len(tmpurl)]
    else:
        tmppath1 = tmpurl
    #
    # Add trailing "/" and leading "www." to urlpath, if necessary
    #
    if tmpurl.endswith("/"):
        tmppath2 = tmppath1
    else:
        tmppath2 = tmppath1 + "/"
    if ("www." in tmppath2):
        urlpath = tmppath2
    else:
        urlpath = "www." + tmppath2
    #
    return urlpath
#
# fetchurl(url) - Fetches the specified url, catches exceptions, and if successful checks if the content is plaintext. 
# Returns success (True or False), exception (True or False), the request response, and error string.
#
def fetchurl(url):
    #
    # Set User Agent to "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0" to avoid 403 errors on some websites.
    #
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0'}
    #
    # Try fetcing the trust.txt file, catch relevant exceptions, if there are no exceptions
    # write the response text to the trust.txt file and check if the content is plaintext.
    #
    success = True
    exception = False
    error = ""
    try:
        r = requests.get(url, timeout=61, verify=False, headers=headers)
    except requests.exceptions.TooManyRedirects as Argument:
        error = "HTTP GET too many redirects exception occurred: " + str(Argument)
        r = "" 
        success = False
        exception = True
    except requests.exceptions.Timeout as Argument:
        error = "HTTP GET time out exception occurred: " + str(Argument)
        r = ""
        success = False
        exception = True
    except requests.exceptions.ConnectionError as Argument:
        error = "HTTP GET connection error exception occurred: " + str(Argument)
        r = ""
        success = False
        exception = True
    else:
        if r.status_code != 200:
            error = "HTTP Status Code: " + str(r.status_code)
            success = False
        else:
            #
            # Check if content type is plaintext.
            #
            success = ("Content-Type" in r.headers) and ("text/plain" in r.headers['Content-Type'])
            #
            # If the content is not plaintext, log an error.
            #
            if not success:
                error = "Content type: " + r.headers['Content-Type']
    #
    # Return results
    #
    return success, exception, r, error
#
# write_error (http, srcpath, attr, refpath, error, errfile) - Write the entry into the error .csv file errfile for the specified srcpath, attr, 
# refpath, and error message.
#
def write_error (http, srcpath, attr, refpath, error, errfile):
    errfile.write (http + srcpath + "," + attr + "," + http + refpath + "," + error + "\n")
#
# write_csv (http, srcpath, attr, refpath, csvfile) - Write the entry into the .csv file csvfile for the specified srcpath, attr, and refpath.
#
def write_csv (http, srcpath, attr, refpath, csvfile):
    csvfile.write (http + srcpath + "," + attr + "," + http + refpath + "\n")
#
# fetchtrust(srcpath,attr,refpath,dirname,filename,csvfile,logfile,errfile) - Fetch a trust.txt file and catch exceptions. If there are no exceptions
# write the contents to the specified directory and filename. Check if the content is plaintext and return success=True. Otherwise, write
# a blank line to the specified directory and filename and return success=False.
#
def fetchtrust (srcpath, attr, refpath, dirname, filename, csvfile, logfile, errfile):
    #
    # Set source and referenced urls.
    #
    http = "https://"
    srcurl = http + srcpath + "trust.txt"
    refurl = http + refpath + "trust.txt"
    #
    # Log fetching the referenced url path
    #
    logfile.write("Fetching: " + refurl + " referenced from " + srcurl + " with attribute \"" + attr + "\"\n")
    #
    # Try using "http" first.
    #
    http = "http://"
    refurl = http + refpath + "trust.txt"
    logfile.write("Trying: " + refurl + "\n")
    #
    success, exception, r, error = fetchurl (refurl)
    if exception:
        #
        # Try using "http" and dropping the "www."
        #
        refurl = http + refpath[4:len(refpath)]
        logfile.write("Trying: " + refurl + "\n")
        success, exception, r, error = fetchurl (refurl)
        #
        if exception:
            #
            # Try using "https"
            #
            http = "https://"
            refurl = http + refpath
            logfile.write("Trying: " + refurl + "\n")
            success, exception, r, error = fetchurl (refurl)
            #
            if exception:
                #
                # Try using "https" and dropping the "www."
                #
                refurl = http + refpath[4:len(refpath)]
                logfile.write("Trying: " + refurl + "\n")
                success, exception, r, error = fetchurl (refurl)    
    if success:
        #
        # Log the status code
        #
        logfile.write ("HTTP Status Code: " + str(r.status_code) + "\n")
        #
        # Write the trust.txt file and log it.
        #
        logfile.write ("Writing HTTP GET response to trust.txt file: " + dirname + "/" + filename + "\n")
        trustfile = open(dirname + "/" + filename,"w")
        trustfile.write(r.text)
        trustfile.close()
        #
        # If the HTTP status code is not OK (not 200), then write to error file and log error.
        #
        if r.status_code != 200:
            write_error ("https://", srcpath, attr, refpath, "HTTP Status Code: " + str(r.status_code), errfile)
            logfile.write ("HTTP Status Code: " + str(r.status_code) + "\n")
            success = False
        else:
            #
            # Check if content type is plaintext.
            #
            success = ("Content-Type" in r.headers) and ("text/plain" in r.headers['Content-Type'])
            #
            # If the content is not plaintext, write to error file and log error.
            #
            if not success:
                write_error ("https://", srcpath, attr, refpath, "Content type: " + r.headers['Content-Type'], errfile)
                logfile.write ("Content type: " + r.headers['Content-Type'] + "\n")
    else:
        #
        # Write a blank trust.txt file, log it, and write to error file.
        #
        write_error ("https://", srcpath, attr, refpath, error, errfile)
        logfile.write ("HTTP GET error: " + error + "\n")
        logfile.write ("Writing blank trust.txt file: " + dirname + "/" + filename + "\n")
        trustfile = open(dirname + "/" + filename,"w")
        trustfile.write("\n")
        trustfile.close()
    #
    return success, r
#
# process(url,dirname,filename,csvfile,logfile) - Process the given url by retrieving the trust.txt 
# file from the given url, write it to the given directory & filename, output the tuple 
# (srcurl,attr,refurl) to the given csvfile, and log process to the given logfile.
#
def process (srcpath, attribute, refpath, dirname, csvfile, logfile, errfile):
    #
    # Specify symmetric and asymmetric attributes, http protocol, and local trust.txt filename.
    #
    symattr = "member,belongto,control,controlledby,vendor,customer"
    asymattr = "social,contact,disclosure"
    http = "https://"
    srcurl = http + srcpath + "trust.txt"
    refurl = http + refpath + "trust.txt"
    filename = refpath.replace("/", "-") + "trust.txt"
    attrcount = 0
    #
    # Log beginning of processing the url
    #
    logfile.write ("BEGIN: " + refurl + "\n")
    #
    # If the specified file doesn't already exist, fetch the url/trust.txt file and parse the contents.
    #
    if not os.path.isfile(dirname + "/" + filename):
        #
        # Fetch the trust.txt file.
        #
        success, r = fetchtrust (srcpath, attribute, refpath, dirname, filename, csvfile, logfile, errfile)
        #
        if (success):
            #
            # If fetch was successful, process each line in the response.
            #
            lines = r.text.splitlines()
            linenum = 0
            for line in lines:
                linenum += 1
                #
                # Remove leading and trailing white space, convert to lowercase, remove any "\x00" chacters.
                #
                tmpline = line.strip().lower().replace("\00","")
                #
                # Skip this line if it is a comment line (begins with "#") or is an empty line
                #
                if tmpline.startswith("#") or tmpline == "":
                    continue
                #
                # Get attribute and referenced url. 
                #
                attr = tmpline.split("=",2)
                if len(attr) == 2:
                    #
                    # If a valid attribute, then increment attribute count, normalize the referenced url, and write 
                    # srcurl,attr,refurl to .csv file. Otherwise, write the invalid attribute error.
                    #
                    if (attr[0] in symattr) or (attr[0] in asymattr):
                        attrcount += 1
                        path = normalize(attr[1])
                        write_csv (http, refpath, attr[0], path, csvfile)
                    else:
                        write_error (http, refpath, attr[0], path, "Invalid attribute" + attr[0] + "at line" + linenum, errfile)
                        logfile.write ("Invalid attribute" + attr[0] + "at line" + linenum + "\n")
                    #
                    # If attribute is a symmetric one, process the referenced url
                    #
                    if attr[0] in symattr:
                        #
                        # Process the referenced url
                        #
                        process (refpath, attr[0], path, dirname, csvfile, logfile, errfile)
        else:
            # Set attrcount to -1 (not zero), prevents no attributes error from also being logged
            #
            attrcount = -1
        #
        # If no attributes were found, log a no attributes error
        #
        if (attrcount == 0):
            write_error ("https://", srcpath, attribute, refpath, refurl + " no attributes found", errfile)
            logfile.write("No attributes found in: " + refurl + "\n")
        #
        # Log completion of processing the url and number of attributes found
        #
        logfile.write ("END: " + refurl + ", number of attributes found = " + str(attrcount) + "\n")
    else:
        #
        # Log url as previously fetched
        #
        logfile.write ("END: " + refurl + " previously fetched\n")
        #
    return
#
# Main program
#
# Ignore warnings
#
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
#
# Set root_url
#
if len(sys.argv) > 1:
    rootpath = sys.argv[1]
else:
    rootpath = "www.journallist.net/"
#
http = "https://"
#
# Create directory name to contain today's webcrawl "Webcrawl-YYYY-MM-DD". If bail if it already
# exists
#
dirname = "Webcrawl-"+time.strftime("%Y-%m-%d")
if (not os.path.isdir(dirname)):
    #
    # Create directory for today's webcrawl
    #
    os.mkdir(dirname)
    #
    # Open .csv and log files
    #
    csvname = dirname + "/" + dirname + ".csv"
    csvfile = open(csvname,"w")
    logname = dirname + "/" + dirname + "-log.txt"
    logfile = open(logname,"w")
    errname = dirname + "/" + dirname + "-err.csv"
    errfile = open(errname,"w")
    #
    # Log start time , directory name, .csv file, and log file names
    #
    logfile.write("START: " + time.asctime( time.localtime(time.time()) ) + "\n")
    logfile.write("Directory name: " + dirname + "\n")
    logfile.write(".csv file name: " + csvname + "\n")
    logfile.write("-err.csv file name: " + errname + "\n")
    logfile.write("Log file name: " + logname + "\n")
    #
    # Write headers to .csv and error files
    #
    csvfile.write ("srcurl,attr,refurl\n")
    errfile.write ("srcurl,attr,refurl,error\n")
    #
    # Normalize the root url
    #
    path = normalize(rootpath)
    #
    # Process the root url
    #
    retcount = process(path, "self", path, dirname, csvfile, logfile, errfile)
    #
    # Log ending time.
    #
    logfile.write("END: " + time.asctime( time.localtime(time.time()) ) + "\n")
    #
    # Close the .csv, log, err files
    #
    csvfile.close()
    logfile.close()
    errfile.close()
else:
    print (dirname, "already exists")