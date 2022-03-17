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
from numpy import triu_indices_from
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
# Because of the vagaries of how urls are used in trust.txt files it is necessary to normalize them so that they can be matched 
# appropriately in the database.
# 
# normalize(url) - Normalize a url to provide just the path in the form "www.domain.com/[path]/" by:
# 1. Remove the leading "http[s]://" if necessary
# 2. Add trailing "/" if necessary
# 3. Convert the domain to lowercase.
# 4. Remove the trailing "trust.txt" if necessary
# 
def normalize (url):
    #
    # Remove leading protocol, if necessary
    #
    if (url.startswith("http://")):
        tmppath1 = url[7:len(url)]
    elif (url.startswith("https://")):
        tmppath1 = url[8:len(url)]
    else:
        tmppath1 = url
    #
    # Add leading "www." to urlpath, if necessary
    #
    if (tmppath1.startswith("www.")):
        tmppath2 = tmppath1
    else:
        tmppath2 = "www." + tmppath1
    #
    # Add trailing "/" to urlpath, if necessary
    #
    if url.endswith("/"):
        tmppath3 = tmppath2
    else:
        tmppath3 = tmppath2 + "/"
    #
    # Split the path into domain and path, convert domain to lowercase.
    #
    splitpath = tmppath3.split("/",1)
    domain = splitpath[0].lower()
    tmppath4 = domain + "/" + splitpath[1]
    #
    # Add or remove trailing "trust.txt[/]" if necessary.
    #
    if (tmppath4.endswith("trust.txt/")):
        urlpath = tmppath4[0:len(tmppath4)-10]
    elif (tmppath4.endswith("trust.txt")):
        urlpath = tmppath4[0:len(tmppath4)-9]
    else:
        urlpath = tmppath4
    #
    # print (url, "normalized to", urlpath)
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
# chkredirect (url,rurl) - Check if the url used in the HTTP GET request is redirected on the returned response url (rurl) and if it is to a
# domain registrar, indicating that the domain has expired. Return redirect, success, exception, error
#
def chkredirect (url,rurl):
    #
    # Set list of domain registrars to check for expired domains.
    #
    registrars = "www.hugedomains.com,www.domain.com,www.godaddy.com,www.namecheap.com,www.name.com,www.enom.com,www.dynadot.com,www.namesilo.com,www.123-reg.co.uk,www.bluehost.com"
    redirect = False
    success = True
    exception = False
    error = ""
    #
    # Remove protocol from url and response.url
    #
    if (url.startswith("http://")):
        http = "http://"
        path = url[len(http):len(url)]
    elif (url.startswith("https://")):
        http = "https://"
        path = url[len(http):len(url)]
    else:
        http = ""
        path = url
    #
    if (rurl.startswith("http://")):
        rhttp = "http://"
        rpath = rurl[len(rhttp):len(rurl)]
    elif (rurl.startswith("https://")):
        rhttp = "https://"
        rpath = rurl[len(rhttp):len(rurl)]
    else:
        rhttp = ""
        rpath = rurl
    #
    # Split into domain and path
    #
    splitpath = path.split("/",1)
    domain = splitpath[0].lower()
    rsplitpath = rpath.split("/",1)
    rdomain = rsplitpath[0].lower()
    #
    # Check for a redirect to another domain.
    #
    redirect = (domain != rdomain)
    if redirect:
        #
        # If redirect domain is a domain registrar, set success to False, exception to True, and set error message.
        #
        if (rdomain in registrars):
            success = False
            exception = True
            error = "HTTP GET domain registration expired - redirects to " + rurl
    #
    return redirect, success, exception, error
#
# fetchtrust (refpath)
#
def fetchtrust (refpath):
    #
    # Try using "http" first.
    #
    http = "http://"
    path = refpath[8:len(refpath)]
    refurl = http + path
    # print ("Trying: ", refurl)
    #
    success, exception, r, error = fetchurl (refurl)
    # print ("Fetch results: ", success, exception, r, error)
    #
    if exception:
        #
        # Try Try using "http" and dropping the "www."
        #
        path = refpath[12:len(refpath)]
        refurl = http + path
        # print ("Trying: ", refurl)
        success, exception, r, error = fetchurl (refurl)
        # print ("Fetch results: ", success, exception, r, error)
        #
        if exception:
            #
            # Try using "https"
            #
            http = "https://"
            path = refpath[8:len(refpath)]
            refurl = http + path
            # print ("Trying: ", refurl)
            success, exception, r, error = fetchurl (refurl)
            # print ("Fetch results: ", success, exception, r, error)
            #
            if exception:
                #
                # Try using "https" and dropping the "www."
                #
                http = "https://"
                path = refpath[12:len(refpath)]
                refurl = http + path
                # print ("Trying: ", refurl)
                success, exception, r, error = fetchurl (refurl)
                # print ("Fetch results: ", success, exception, r, error)
                #
    #
    # Fall through to here after trying the different url forms.
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
# Check if top level domains match
#
def checktld (url1, url2):
    tmpurl = url1
    if ("trust.txt" in tmpurl):
        length = len(tmpurl) - 9
    else:
        length = len(tmpurl)
    if ("http://" in tmpurl):
        tmppath1 = tmpurl[7:length]
    elif ("https://" in tmpurl):
        tmppath1 = tmpurl[8:length]
    else:
        tmppath1 = tmpurl
    tmpurl = url2
    if ("trust.txt" in tmpurl):
        length = len(tmpurl) - 9
    else:
        length = len(tmpurl)
    if ("http://" in tmpurl):
        tmppath2 = tmpurl[7:length]
    elif ("https://" in tmpurl):
        tmppath2 = tmpurl[8:length]
    else:
        tmppath2 = tmpurl
    return (tmppath1 == tmppath2)
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
            # Remove leading and trailing white space, and remove any non-ASCII chacters (using encode to create bytes object and decode to
            # convert bytes object back to str), remove any null characters "\00"
            #
            bytesline = line.strip().encode("ascii","ignore")
            tmp1line = bytesline.decode("ascii","ignore")
            tmpline = tmp1line.replace("\00","")
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
                # If it is a symmetric attribute, then normalize the referenced url and check for the referenced trust.txt file. 
                # Else if it is not an assymetric attribute, print an invalid attribute error.
                #
                if (attr[0] in symattr):
                    attrcount += 1
                    path = normalize(attr[1])
                    url = "https://" + path + "trust.txt"
                    success, exception, r, error = fetchtrust(url)
                    #
                    # If not successful print an error
                    #
                    if not success:
                        #
                        # If there was an exception, server was unreachable. Otherwise, 
                        #
                        if exception:
                            print ("Error at line:",linenum,line.strip(),"- unable to connect with server -",path,"-",error)
                            whoislist.append(path[4:len(path)-1])
                        else:
                            print ("Error at line:",linenum,line.strip(),"- trust.txt file not found -",url,"-",error)
                    #
                    # If there there wasn't an exception, check for redirect.
                    #
                    if not exception:
                        redirect, success, exception, error = chkredirect(url, r.url)
                        if redirect:
                            print ("Warning at line:",linenum,line.strip(),"-",url, "redirects to", r.url)
                            if exception:
                                print ("Error at line:",linenum,line.strip(),"-",error)
                #
                elif (attr[0] not in asymattr):
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
