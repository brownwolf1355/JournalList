#!/usr/local/bin/python3.10
#
# JournalList.net QA script to check the specified trust.txt file.
#
# Name - qa_trust_txt.py trust.txt [srcurl webcrawl.csv]
# Synopsis - qa_trust_txt.py trust.txt
#   trust.txt - The trust.txt file to check.
#   srcurl - Optional, the URL to be used as the srcurl, to check against the .csv file
#   webcrawl.csv - Optional, the .csv file containing the results of a webcrawl of all published trust.txt files
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import requests
#
# import ssl
# from urllib3.poolmanager import PoolManager
# from requests.adapters import HTTPAdapter
#
# Transport adapter" that allows us to use SSLv 1.2 and later
# From: https://docs.python-requests.org/en/master/user/advanced/#example-specific-ssl-version
# and: https://stackoverflow.com/questions/29153271/sending-tls-1-2-request-in-python-2-6
#
# class Ssl3HttpAdapter(HTTPAdapter):
#     def init_poolmanager(self, connections, maxsize, block=False):
#         self.poolmanager = PoolManager(
#             num_pools=connections, maxsize=maxsize,
#             block=block, ssl_version=ssl.PROTOCOL_SSLv23 | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
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
    http = "http://"
    refurl = http + refpath[8:len(refpath)]
    # print ("Trying: ", refurl)
    #
    success, exception, r, error = fetchurl (refurl)
    # print ("Fetch results: ", success, exception, r, error)
    #
    if exception:
        #
        # Try Try using "http" and dropping the "www."
        #
        refurl = "http://" + refpath[12:len(refpath)]
        # print ("Trying: ", refurl)
        success, exception, r, error = fetchurl (refurl)
        # print ("Fetch results: ", success, exception, r, error)
        #
        if exception:
            #
            # Try using "https"
            #
            refurl = refpath
            # print ("Trying: ", refurl)
            success, exception, r, error = fetchurl (refurl)
            # print ("Fetch results: ", success, exception, r, error)
            #
            if exception:
                #
                # Try using "https" and dropping the "www."
                #
                refurl = "https://" + refpath[12:len(refpath)]
                # print ("Trying: ", refurl)
                success, exception, r, error = fetchurl (refurl)
                # print ("Fetch results: ", success, exception, r, error)
                #
    return success, exception, r, error
#
# Read the Webcrawl.csv file and filter out the "control" and "controlledby" entries.
#
def readcsv (filename):
    file = open(filename,"r")
    lines = file.readlines()
    file.close()
    srclist = []
    attrlist = []
    reflist = []
    for line in lines:
        temp = line.split(",",3)
        # print ("readcsv: temp", temp)
        if (temp[1] == "control") or (temp[1] == "controlledby") or (temp[1] == "social"):
            srclist.append(temp[0].strip())
            attrlist.append(temp[1].strip())
            reflist.append(temp[2].strip())
    return srclist, attrlist, reflist
#
# Check if attr and refurl are in .csv file with a different srcurl.
#
def checkattr (srcurl, attr, refurl, srclist, attrlist, reflist, linenum):
    #
    # Loop through lists checking if attr, refurl pair present for a different srcurl and print warning.
    #
    for index in range(len(reflist)):
        # print ("checkattr: srclist, attrlist, reflist, index -", srclist[index], ",", attrlist[index], ",", reflist[index])
        if (srcurl != srclist[index]) and (attr == attrlist[index]) and (refurl == reflist[index]):
            temp = srclist[index] + "," + attrlist[index] + "," + reflist[index]
            print ("Warning at line:", linenum, "attribute and refurl also used in:", temp)
#
# Main program
#
# Ignore warnings
#
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
#
# Set trust.txt filename.
#
if len(sys.argv) > 1:
    filename = sys.argv[1]
    if len(sys.argv) > 3:
        checkcsv = True
        srcurl = normalize(sys.argv[2])
        srclist, attrlist, reflist = readcsv(sys.argv[3])
    else:
        checkcsv = False
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
        file.close()
        #
        linenum = 0
        attrcount = 0
        jlfound = False
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
            # Get attribute and referenced url. Ignore attributes with null references, e.g. "control="
            #
            attr = tmpline.split("=",2)
            if (len(attr) == 2) and (attr[1] != ""):
                #
                # If srcurl and .csv file specified, check to see if present in .csv file.
                #
                if (checkcsv):
                    if (attr[0] == "control") or (attr[0] == "controlledby") or (attr[0] == "social"):
                        refurl = normalize(attr[1])
                        checkattr ("https://" + srcurl, attr[0], "https://" + refurl, srclist, attrlist, reflist, linenum)
                #
                # If it is a symmetric attribute, then normalize the referenced url and check the referenced trust.txt file. 
                # If it is an asymmetric attribute, then normalize the referenced url and check the referenced url for html text.
                # Otherwise, write the invalid attribute error.
                #
                if (attr[0] in symattr):
                    attrcount += 1
                    path = normalize(attr[1])
                    server = "https://" + path
                    url = server + "trust.txt"
                    success, exception, r, error = fetchtrust(url)
                    if not success:
                        if exception:
                            print ("Error at line:",linenum,line.strip(),"- unable to connect with server -",server,"-",error)
                            whoislist.append(path[4:len(path)-1])
                        else:
                            print ("Error at line:",linenum,line.strip(),"- missing trust.txt file -",url,"-",error)
                elif (attr[0] in asymattr):
                    attrcount += 1
                    path = normalize(attr[1])
                    success, exception, r, error = fetchtrust("https://" + path)
                    if not success and not exception and (not (("Content-Type" in r.headers) and ("text/html" in r.headers['Content-Type']))):
                        print ("Error at line:",linenum,line.strip(),"- missing trust.txt file -",url,"-",error)
                    elif exception:
                        print ("Error at line:",linenum,line.strip(),"- unable to connect with server -",server,"-",error)
                        whoislist.append(path[4:len(path)-1])
                else:
                    print ("Invalid attribute at line:",linenum,attr[0])
        #
        # Check if no attributes found
        #
        if (attrcount == 0):
            print ("No attributes found")
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
    print ("No trust.txt file specified")
