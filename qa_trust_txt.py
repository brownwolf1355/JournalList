#!/usr/local/bin/python3.10
#
# JournalList.net QA script to check the specified trust.txt file.
#
# Name - qa_trust_txt.py
# Synopsis - qa_trust_txt.py trust.txt
#   trust.txt - The trust.txt file to check.
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
    # Log fetching the url.
    #
    # print("Fetching: ", url)
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
        r = requests.get(url, timeout=5, verify=False, headers=headers)
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
# fetchtrust (refpath)
#
def fetchtrust (refpath):
    #
    # Try using "http" first.
    #
    refurl = "http://" + refpath[8:len(refpath)]
    #
    success, exception, r, error = fetchurl (refurl)
    # print ("Fetch results: ", success, exception, r, error)
    #
    if exception:
        #
        # Try Try using "http" and dropping the "www."
        #
        refurl = "http://" + refpath[12:len(refpath)]
        success, exception, r, error = fetchurl (refurl)
        # print ("Fetch results: ", success, exception, r, error)
        #
        if exception:
            #
            # Try using "https"
            #
            refurl = refpath
            success, exception, r, error = fetchurl (refurl)
            # print ("Fetch results: ", success, exception, r, error)
            #
            if exception:
                #
                # Try using "https" and dropping the "www."
                #
                refurl = "https://" + refpath[12:len(refpath)]
                success, exception, r, error = fetchurl (refurl)
    return success, exception, r, error
#
# Main program
#
# Ignore warnings
#
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
#
# Set url
#
if len(sys.argv) > 1:
    filename = sys.argv[1]
    #
    # Check if file exists.
    #
    if(os.path.isfile(filename)):
        symattr = "member,belongto,control,controlledby,vendor,customer"
        asymattr = "social,contact,disclosure"
        whoislist = []
        #
        # Open file and read it.
        #
        file = open(filename,"r")
        lines = file.readlines()
        linenum = 0
        jlfound = False
        #
        # Close trust.txt file.
        #
        file.close()
        #
        # Parse trust.txt file
        #
        for line in lines:
            linenum += 1
            #
            # Remove leading and trailing white space, convert to lowercase, remove any "\x00" chacters.
            #
            tmpline = line.strip().lower().replace("\00","")
            #
            # Check if "journallist.net" is in file.
            if (not jlfound):
                jlfound = "journallist.net" in tmpline
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
                # If it is a symmetric attribute, then normalize the referenced url and check the referenced trust.txt file. 
                # If it is an asymmetric attribute, then normalize the referenced url and check the referenced url for html text.
                # Otherwise, write the invalid attribute error.
                #
                if (attr[0] in symattr):
                    path = normalize(attr[1])
                    success, exception, r, error = fetchtrust("https://" + path + "trust.txt")
                    if not success:
                        print ("Error at line",linenum,": ",line.strip(),"-",error)
                        if exception:
                            whoislist.append(path[4:len(path)-1])
                elif (attr[0] in asymattr):
                    path = normalize(attr[1])
                    success, exception, r, error = fetchtrust("https://" + path)
                    if not success and not exception and (not (("Content-Type" in r.headers) and ("text/html" in r.headers['Content-Type']))):
                        print ("Error at line",linenum,": ",line.strip(),"-",error)
                    elif exception:
                        whoislist.append(path[4:len(path)-1])
                else:
                    print ("Invalid attribute at line",linenum,":",attr[0])
        #
        # Write the list of domains that raised exceptions.
        #
        if len(whoislist) > 0:
            whoisfile = open("whoislist.txt","w")
            for domain in whoislist:
                whoisfile.write(domain + "\n")
            whoisfile.close()
        #
        # Check if "journallist.net" found.
        #
        if (not jlfound):
            print ("Error at line",linenum,": file does not contain journallist.net")
    else:
        print (filename, "does not exist")
else:
    print ("No file specified")
