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
# 3. It generates a Webcrawl-YYYY-MM-DD-redirects.csv file that provides a list of redirects discovered.
# 4. It generates a Webcrawl-YYYY-MM-DD-log.txt file that provides useful debug information.
# 5. It generates a Webcrawl-YYYY-MM-DD-err.csv file that lists all of the urls that generated
#    errors under four columns:
#    - the source url referencing the url in error
#    - the attribute ussed in the reference
#    - url is the url that generated the error
#    - error is the error status code or "HTML" if the content is an HTML page or "exception"
#      if the request throws and exception.
#
# The webcrawler downloads the trust.txt file for the ROOT_URL, then extracts all "member", 
# "belongto", "vendor", "consumer", "control", and "controlledby" referenced URLs and recursively
# downloads and process each.
# 
# To insure that source urls and referenced urls in symmetric attributes match it is necessary to normalizes all these URLs to 
# be of the form http[s]://www.domain.com/, (e.g., all lowercase, with leading "www." and trailing "/"). Referenced urls in asymmetric 
# attributes are not converted to all lowercase.
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import time
import requests
from urllib.parse import urlparse
#
# Skip any well-known resources that begin with any of the following strings
#
well_known_skip =[
    "assets.",
    "m.",
    "storyconsole."
]
#
# Top level country domains
#
countrytld = [
    "ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az",
    "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz",
    "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz",
    "de", "dj", "dk", "dm", "do", "dz",
    "ec", "ee", "eg", "er", "es", "et", "eu",
    "fi", "fj", "fk", "fm", "fo", "fr",
    "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy",
    "hk", "hm", "hn", "hr", "ht", "hu", 
    "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it",
    "je", "jm", "jo", "jp",
    "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz",
    "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly",
    "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz",
    "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz",
    "om",
    "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py",
    "qa",
    "re", "ro", "rs", "ru", "rw",
    "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz",
    "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw","tz",
    "ua", "ug", "uk", "um", "us", "uy", "uz",
    "va", "vc", "ve", "vg", "vi", "vn", "vu",
    "wf", "ws"
]
#
# Because of the vagaries of how urls are used in trust.txt files it is necessary to normalize them so that they can be matched 
# appropriately in the JournalList ecosystem database.
# 
# normalize (url) - Normalize the input url and return base domain (e.g., journallist.net), subdomain (if any), and subdirectory (if any).
#
def normalize (url):
    #
    # Parse the url
    #
    o = urlparse(url)
    #
    # If no scheme is provided, then domain is contained in o.path up to a "/" and subdirectory = o.path from "/" to the remainder, otherwise take them from urlparse results
    #
    if o.scheme == "":
        s = o.path.split("/",1)
        domain = s[0]
        if (len(s) > 1):
            subdir = s[1]
        else:
            subdir = ""
    else:
        subdir = o.path
        domain = o.netloc
    #
    # If subdirectory is just "/" return null
    #
    if subdir == "/":
        subdir = ""
    #
    # Get base domain, typically the last two elements of the netloc, unless top level domain is a country code, in which case it is the last three elements of the netloc
    #
    s = domain.split(".")
    slen = len(s)
    if (s[slen-1] in countrytld) and (slen > 2) and (s[slen-3] != "www"):
        dlen = 3
        domain = s[slen - 3] + "." + s[slen - 2] + "." + s[slen - 1]
    else:
        if slen > 1:
            dlen = 2
            domain = s[slen - 2] + "." + s[slen - 1]
        else:
            dlen = 1
            domain = s[0]   
    #
    domain = domain.lower()
    #
    # Get subdomain if there is one (elements of netloc preceeding base domain)
    #
    subdom = ""
    n = slen - dlen
    if n > 0:
        i = 0
        subdom = s[i]
        while i < n - 1:
            i = i + 1
            subdom = subdom + "." + s[i]
    #
    return domain, subdom, subdir
#
# fetchurl(url) - Fetches the specified url, catches exceptions, and if successful checks if the content is plaintext. 
# Returns success (True or False), exception (True or False), the request response, and error string.
# 
# Valid success & exception states (cannot have both success = True and exception = True):
#
#    success = False, exception = False - 404 error or not plaintext.
#    success = True,  exception = False - trust.txt file found
#    success = False, exception = True  - connection error occured trying to connect to site
#
def fetchurl(url):
    #
    # Set User Agent to "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0" to avoid 403 errors on some websites.
    #
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0'}
    #
    # Set User Agent to "Mozilla/5.0 (compatible; JournalListBot/0.1; +https://journallist.net/JournalListBot.html)" to avoid 403 errors on some websites.
    #
    # headers = {'user-agent': 'Mozilla/5.0 (compatible; JournalListBot/0.1; +https://journallist.net/JournalListBot.html)'}
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
# write_error (srcurl, attr, refurl, error, errfile) - Write the entry into the error .csv file errfile for the specified srcpath, attr, 
# refpath, and error message.
#
def write_error (srcurl, attr, refurl, error, errfile):
    errfile.write (srcurl + "," + attr + "," + refurl + "," + error + "\n")
#
# write_csv (srcurl, attr, refurl, csvfile) - Write the entry into the .csv file csvfile for the specified srcpath, attr, and refpath.
#
def write_csv (srcurl, attr, refurl, csvfile):
    csvfile.write (srcurl + "," + attr + "," + refurl + "\n")
#
# write_csv_asym (srcurl, attr, refurl, csvfile) - Write the asymmetric attribute entry (don't prepend http) into the .csv file csvfile for the specified 
# srcpath, attr, and refpath.
#
def write_csv_asym (srcurl, attr, refurl, csvfile):
    csvfile.write (srcurl + "," + attr + "," + refurl + "\n")
#
# fetchtrust (srcdomain,attr,refdomain,dirname,filename,csvfile,logfile,errfile) - Fetch a trust.txt file and catch exceptions. If there are no exceptions
# write the contents to the specified directory and filename. Check if the content is plaintext and return success=True. Otherwise, write
# a blank line to the specified directory and filename and return success=False.
#
def fetchtrust (srcdomain, attr, refdomain, dirname, filename, redirfile, logfile, errfile):
    #
    # Set list of domain registrars to check for expired domains.
    #
    registrars = "www.hugedomains.com,www.domain.com,www.godaddy.com,www.namecheap.com,www.name.com,www.enom.com,www.dynadot.com,www.namesilo.com,www.123-reg.co.uk,www.bluehost.com"
    #
    # Set source and referenced urls.
    #
    srcurl = "https://www." + srcdomain + "/trust.txt"
    refurl = "https://www." + refdomain + "/trust.txt"
    #
    # Log fetching the referenced url path
    #
    logfile.write("Fetching: " + refurl + " referenced from " + srcurl + " with attribute \"" + attr + "\"\n")
    #
    # Try using "http"
    #
    refurl = "http://" + refdomain + "/trust.txt"
    logfile.write("Trying: " + refurl + "\n")
    #
    success, exception, r, error = fetchurl (refurl)
    if exception or r.status_code == 404:
        #
        # Try using "http" and adding "/.well-known"
        #
        refurl = "http://" + refdomain + "/.well-known/trust.txt"
        logfile.write("Trying: " + refurl + "\n")
        success, exception, r, error = fetchurl (refurl)
    #
    # Fall through to here after trying different url forms
    #
    if success:
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
            write_error (srcurl, attr, refurl, "HTTP Status Code: " + str(r.status_code), errfile)
            logfile.write ("HTTP Status Code: " + str(r.status_code) + "\n")
            success = False
        else:
            #
            # Log the content type.
            #
            logfile.write (refurl + " content type: " + r.headers['Content-Type'] + "\n")
            #
            # Check if content type is plaintext.
            #
            success = ("Content-Type" in r.headers) and ("text/plain" in r.headers['Content-Type'])
            #
            # If the content is not plaintext, write to error file and log error.
            #
            if not success:
                write_error (srcurl, attr, refurl, "Content type: " + r.headers['Content-Type'], errfile)
        #
        # Log the status code
        #
        logfile.write ("HTTP Status Code: " + str(r.status_code) + "\n")
        #
        # Check if redirected to another domain by checking that normalized versions of the refurl and r.url do not match.
        #
        domain1, subdom1, subdir1 = normalize (refurl)
        domain2, subdom2, subdir2 = normalize (r.url)
        #
        if (domain1 != domain2):
            #
            # Log redirect and write to redirect file.
            #
            logfile.write (refurl + " redirects to " + r.url + "\n")
            redirfile.write (refurl + "," + r.url + "\n")
            #
            # Check if redirect domain is a domain registrar, set success to False and set error message.
            #
            if (domain2 in registrars):
                success = False
                error = "HTTP GET domain registration expired redirects to " + r.url
            #
            # Check if the fetch redirects to an existing file, if so log it has already been fetched and set success to False so that contents are not processed again.
            #
            rfilename = "www." + domain2 + "-trust.txt"
            if os.path.isfile(dirname + "/" + rfilename):
                #
                # Log url as previously fetched
                #
                logfile.write (r.url + " previously fetched\n")
                success = False
    else:
        #
        # Write a blank trust.txt file, log it, and write to error file.
        #
        write_error (srcurl, attr, refurl, error.replace(",",""), errfile)
        logfile.write ("HTTP GET error: " + error + "\n")
        logfile.write ("Writing blank trust.txt file: " + dirname + "/" + filename + "\n")
        trustfile = open(dirname + "/" + filename,"w")
        trustfile.write("\n")
        trustfile.close()
    #
    return success, r
#
# process(srcdomain, attribute, refdomain, dirname, csvfile, logfile, errfile) - Process the given refdomain by retrieving the trust.txt 
# file from the given redomain, write it to the given directory & filename, output the tuple [srcurl,attr,refurl] to the given csvfile, 
# log process to the given logfile, and errors to the given errfile.
#
def process (srcdomain, attribute, refdomain, dirname, csvfile, redirfile, logfile, errfile):
    #
    # Specify symmetric and asymmetric attributes
    #
    symattr = "member,belongto,control,controlledby,vendor,customer"
    asymattr = "social,contact,disclosure"
    #
    # Only process the refdomain if the attribute is a symmetric attribute and the srcdomain is not the same as the refdomain
    #
    if (attribute == "self") or ((attribute in symattr) and (srcdomain != refdomain)):
        #
        # Set srcurl and refurl to standard format (https://www.domain/, e.g., https://www.journallist.net/)
        #
        srcurl = "https://www." + srcdomain + "/"
        refurl = "https://www." + refdomain + "/"
        #
        # Set filename to standard format (www.domain-trust.txt, e.g., www.journallist.net-trust.txt)
        #
        filename = "www." + refdomain + "-trust.txt"
        #
        # Set attribute count to zero
        #
        attrcount = 0
        #
        # Log beginning of processing the url
        #
        logfile.write ("BEGIN: " + refurl + "trust.txt\n")
        #
        # If the specified file doesn't already exist, fetch the url/trust.txt file and parse the contents.
        #
        if not os.path.isfile(dirname + "/" + filename):
            #
            # Fetch the trust.txt file.
            #
            success, r = fetchtrust (srcdomain, attribute, refdomain, dirname, filename, redirfile, logfile, errfile)
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
                    # Remove leading and trailing white space, and remove any non-ASCII chacters (using encode to create bytes object and decode to
                    # convert bytes object back to str), remove any null characters "\00", or tab "\t", or spaces.
                    #
                    bytesline = line.strip().encode("ascii","ignore")
                    tmp1line = bytesline.decode("ascii","ignore")
                    tmpline = tmp1line.replace("\00","")
                    tmpline1 = tmpline.replace("\t","")
                    tmpline = tmpline1.replace(" ","")
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
                        # If a symmetric attribute then normalize the referenced url, otherwise the reference url should remain unmodified.
                        #
                        if (attr[0] in symattr):
                            attrcount += 1
                            #
                            # Normalize the referenced url
                            #
                            domain, subdomain, subdir = normalize(attr[1])
                            #
                            # If subdomain is empty, begin url with "www", if subdomain begins with "www" then use subdomain, else use subdomain
                            #
                            if subdomain == "":
                                url = "https://www"
                            elif subdomain.startswith("www"):
                                url = "https://" + subdomain
                            else:
                                url = "https://" + subdomain
                            #
                            # Add domain to url
                            #
                            url = url + "." + domain
                            #
                            # Add subdirectory if not empty
                            #
                            if subdir != "":
                                if subdir.startswith("/"):
                                    url = url + subdir
                                else:
                                    url = url + "/" + subdir
                            #
                            # Add trailing "/" if not present
                            #
                            if not url.endswith("/"):
                                url = url + "/"
                            #
                            # Write the tuple [srcrul, attribute, refurl] in standard format to the .csv file
                            #
                            write_csv (refurl, attr[0], url , csvfile)
                        elif (attr[0] in asymattr):
                            attrcount += 1
                            #
                            # Write the tuple [srcrul, attribute, refurl] in standard format to the .csv file
                            #
                            url = attr[1]
                            write_csv_asym (refurl, attr[0], url, csvfile)
                        else:
                            #
                            # Write invalid attribute error to log and error files
                            #
                            write_error (refurl, attr[0], url, "Invalid attribute" + attr[0] + "at line " + str(linenum), errfile)
                            logfile.write ("Invalid attribute" + attr[0] + "at line " + str(linenum) + "\n")
                        #
                        # If attribute is a symmetric one, process the referenced domain
                        #
                        if attr[0] in symattr:
                            #
                            # Recursively process the referenced domain, remember refdomain is now the srcdomain
                            #
                            process (refdomain, attr[0], domain, dirname, csvfile, redirfile, logfile, errfile)
            else:
                # Set attrcount to -1 (not zero), prevents no attributes error from also being logged
                #
                attrcount = -1        
            #
            # If no attributes were found, log a no attributes error
            #
            if (attrcount == 0):
                write_error (srcurl, attribute, refurl, refurl + "trust.txt no attributes found", errfile)
                logfile.write("No attributes found in: " + refurl + "\n")
            #
            # Log completion of processing the url and number of attributes found
            #
            logfile.write ("END: " + refurl + "trust.txt, number of attributes found = " + str(attrcount) + "\n")
        else:
            #
            # Log url as previously fetched
            #
            logfile.write ("END: " + refurl + "trust.txt previously fetched\n")
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
    rootdomain = sys.argv[1]
else:
    rootdomain = "journallist.net"
#
rooturl = "https://" + rootdomain
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
    redirname = dirname + "/" + dirname + "-redirects.csv"
    redirfile = open(redirname,"w")
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
    # Write headers to .csv, redirects, and error files
    #
    csvfile.write ("srcurl,attr,refurl\n")
    redirfile.write("srcurl,redirect\n")
    errfile.write ("srcurl,attr,refurl,error\n")
    #
    # Normalize the root url
    #
    path = normalize(rooturl)
    #
    # Process the root url
    #
    retcount = process(rootdomain, "self", rootdomain, dirname, csvfile, redirfile, logfile, errfile)
    #
    # If well-known.dev resource list obtained from (https://well-known.dev/?q=resource%3Atrust.txt+is_base_domain%3Atrue) exists process each entry.
    # Each entry is a tuple of [rank, domain, resource, status, scan_dt, simhash]
    #
    resname = "resources.csv"
    if os.path.isfile(resname):
        #
        logfile.write("BEGIN: processing well-known.dev resource list\n")
        resfile = open(resname,"r")
        #
        # Read the lines of the resource file
        #
        lines = resfile.readlines()
        #
        # Process the domain for each line.
        #
        for line in lines:
            tuple = line.split(",",5)
            if tuple[0] != "rank":
                domain, subdomain, subdir = normalize(tuple[1])
                if (subdomain != ""):
                    domain = subdomain + "." + domain
                #
                # Check if subdomain matches one of the subdomains that shoud be skipped
                #
                found = False
                for i in range(0,len(well_known_skip)):
                    if (subdomain == well_known_skip[i]):
                        found = True
                #
                if not found:
                    retcount = process(domain, "self", domain, dirname, csvfile, redirfile, logfile, errfile)
    #
    # Log ending time.
    #
    logfile.write("END: " + time.asctime( time.localtime(time.time()) ) + "\n")
    #
    # Close the .csv, log, err files
    #
    csvfile.close()
    redirfile.close()
    logfile.close()
    errfile.close()
else:
    print (dirname, "already exists")