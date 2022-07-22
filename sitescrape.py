#!/usr/local/bin/python3.10
#
# JournalList.net website scraper to scan all sites in a list and find all social, contact, and vendor links.
#
# usage: sitescrape.py [-h] [-v] [-s] [-d DIRNAME] [-w WEBCRAWL] url_or_filename
#
# Scrapes websites to discover: 'name', 'contact', 'social', and 'copyright' and writes trust.txt file. Optionally, checks webcrawler ouptut for additional 'belongto' entries.
#
# positional arguments:
#   url_or_filename       url to scrape or name of a .csv file containing a list of urls to scape
#
# options:
#   -h, --help            show this help message and exit
#   -v, --verbose         increase output verbosity
#   -s, --save            save HTML from the website
#   -j, -J                force trust.txt files to include "https://www.journallist.net/"
#   -d DIRNAME            name of directory to write output, defualt to current directory
#   -w WEBCRAWL           name of webcrawler output directory to check for belongto entries
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import requests
import re
import html
from bs4 import BeautifulSoup
import argparse
from html.parser import HTMLParser
from urllib.parse import unquote
# 
# Define global variables
#
# Define set of error text to check in returned HTML text
#
errors = [
    "Page Not Found",
    "Site Not Found",
    "Access denied",
    "Server Error",
    "Private Site",
    "Under Construction",
    "OH SNAP!",
    "ErrorPageController"
    ]
#
# Define list of domain registrars to check for expired domains
#
registrars = [
    "www.hugedomains.com",
    "www.domain.com",
    "www.godaddy.com",
    "www.namecheap.com",
    "www.name.com",
    "www.enom.com",
    "www.dynadot.com",
    "www.namesilo.com",
    "www.123-reg.co.uk",
    "www.bluehost.com"
    ]
#
# Define list of known vendors, add to this list to add new vendors
#
vendors = [
    "bulletlink.com",
    "creativecirclemedia.com",
    "dirxion.com",
    "going1up.com",
    "our-hometown.com",
    "townnews.com",
    "887media.com",
    "crowct.com",
    "etypeservices.com",
    "etypeservices.net",
    "surfnewmedia.com",
    "websitesfornewspapers.com",
    "xyzscripts.com",
    "publishwithfoundation.com",
    "socastdigital.com",
    "creativecirclemedia.com",
    "disqus.com",
    "locablepublishernetwork.com",
    "metropublisher.com",
    "intertechmedia.com",   
    "tecnavia.com"
    ]
#
# Define media conglomerates that publish multiple brands on different domains, add to this list to add new media conglomerates
#
chains = {
    "Advance Local Media":"https://www.advancelocal.com/",
    "Allen Media Broadcasting":"https://allenmediabroadcasting.com/",
    "Alpha Media":"https://www.alphamediausa.com/",
    "C&S Media":"https://csmediatexas.com/",
    "CherryRoad Media":"https://cherryroad-media.com/",
    "Colorado Community Media":"https://coloradocommunitymedia.com/",
    "Cumulus Media":"https://www.cumulusmedia.com/",
    "Ellington":"http://www.connectionnewspapers.com/",
    "Gannett":"https://www.gannett.com/",
    "Gray Television":"https://www.gray.tv/",
    "Hearst":"https://www.hearst.com/",
    "Independent Newsmedia":"https://newszap.com/",
    "Lee Enterprises":"https://lee.net/",
    "MediaNews Group":"https://www.medianewsgroup.com/",
    "Mountain Media":"https://mountainmedianews.com/",
    "News Media Corporation":"http://www.newsmediacorporation.com/",
    "Outdoor Sportsman Group":"https://www.outdoorsg.com/",
    "Penske Media Corporation":"https://pmc.com/",
    "Postmedia Network":"https://www.postmedia.com/",
    "Scripps Media":"https://scripps.com/",
    "Swift Communications":"https://www.swiftcom.com/",
    "Trusted Media Brands":"https://www.trustedmediabrands.com/",
    "Vox Media":"https://corp.voxmedia.com/"
    }
#
# Define list of social networks, add to this list to add new social networks
#
socials = [
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "youtube.com",
    "linkedin.com",
    "pinterest.com"
    ]
#
# Define url exceptions, primarily to catch social network references that aren't the actual handle for the organization
#
exceptions = [
    "//staticxx.facebook.com",
    "//staticxx.facebook.com/",
    "http://facebook.com",
    "https://facebook.com",
    "http://www.facebook.com",
    "https://www.facebook.com",
    "//facebook.com",
    "//www.facebook.com",
    "//graph.facebook.com",
    "facebook.com/profile.ph",
    "http://instagram.com",
    "https://instagram.com",
    "http://www.instagram.com",
    "https://www.instagram.com",
    "//instagram.com",
    "//platform.instagram.com",
    "http://twitter.com",
    "https://twitter.com",
    "http://www.twitter.com",
    "https://www.twitter.com",
    "//twitter.com",
    "//platform.twitter.com",
    "//syndication.twitter.com",
    "//youtube.com",
    "http://linkedin.com",
    "https://linkedin.com",
    "http://www.linkedin.com",
    "https://www.linkedin.com",
    "//linkedin.com",
    "//platform.linkedin.com",
    "http://pinterest.com",
    "https://pinterest.com",
    "http://www.pinterest.com",
    "https://www.pinterest.com",
    "https://www.pinterest.com/",
    "https://www.pinterest.com/pin/create/button/",
    "//pinterest.com",
    "//assets.pinterest.com",
    "//api.pinterest.com"
    ]
#
# Define embedded exceptions
#
embedded = [
    "/wp-content",
    "share",
    "/intent",
    "appId",
    "/pin/create/",
    "/media/set",
    "youtube.com/watch",
    "/favicon.",
    "//static.xx.fbcdn.net/",
    "squarespace.com/",
    "BOOMR.url",
    "-contact-",
    "-about-",
    "abouts",
    "-connect",
    "contact-form"
    ]
#
# Define home page variants (ignoring case) for removal from site name
#
homepage = ["home page [-|\|]", "home page$", "homepage [-|\|]", "homepage$", "home [-|\|]", "[-|\|] home$"]
#
# Define various forms of "contact" in contact urls
#
contactlist = ["contact-us", "about-us", "contact", "about", "connect", "kontakt", "mailto:"]
#
# Set verbose and save modes to False
#
verbose = False
save = False
redo = False
#
# Declare global href and datalist to hold return values from HTML parser handler.
#
global href
datalist = []
#
# Define HTMLparser handlers
#
class MyHTMLParser(HTMLParser):
    #
    def handle_starttag(self, tag, attrs):
        global href
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href" and attr[1] != "":
                    href = attr[1]
                    if verbose:
                        print ("href = ", href)
    #
    def handle_data(self, data):
        global datalist
        datalist.append(data)
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
    if (verbose):
        print ("fetchurl:url =", url)
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
    #
    if (verbose):
        print ("fetcurl:success = ", success, "exception = ", exception, "error = ", error)
    #
    # Return results
    #
    return success, exception, r, error
#
# write_trust_txt (website, contact, links, vendor, copyright, cntrldby, csvfile) - Write the trust.txt file.
#
def write_trust_txt (name, website, contact, links, vendor, copyright, controls, cntrldby, members, belongtos, output):
    #
    # Define trust.txt file header and commment text
    #
    header = "# NAME trust.txt file\n#\n# For more information on trust.txt see:\n# 1. https://journallist.net - Home of the trust.txt specification\n# 2. https://datatracker.ietf.org/doc/html/rfc8615 - IETF RFC 8615 - Well-Known Uniform Resource Identifiers (URIs)\n# 3. https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml - IANA's list of registered Well-Known URIs\n#\n"
    contolledby = "# NAME is controlled by the following organization\n#\n"
    control = "# NAME controls the following organization\n#\n"
    belongto = "# NAME belongs to the following organizations\n#\n"
    member = "# NAME has the following organizations as members\n#\n"
    social = "# NAME social networks\n#\n"
    vndr = "#\n# NAME vendors\n#\n"
    cntct = "#\n# NAME contact info\n#\n"
    #
    # Write header
    #
    output.write (header.replace("NAME",name))
    #
    # If there is are sites that are controlled, write the "control="" entries
    #
    if len(controls) > 0:
        output.write (control.replace("NAME",name))
        for cntrl in controls:
            output.write ("control=" + cntrl + "\n")
        output.write("#\n")
    #
    # If there is a controlling site, write the "controlledby="" entry
    #
    if cntrldby != "":
        output.write (contolledby.replace("NAME",name))
        output.write ("controlledby=" + cntrldby + "\n#\n")
    #
    # If there are members, write the "member=" entries
    #
    if len(members) > 0:
        output.write (member.replace("NAME",name))
        for membr in members:
            output.write ("member=" + membr + "\n")
        output.write("#\n")
    #
    # Write "belongto="" entry
    #
    output.write (belongto.replace("NAME",name))
    if len(belongtos) > 0:
        for blongto in belongtos:
            output.write ("belongto=" + blongto + "\n")
    else:
        output.write ("# belongto=  \n")
    output.write("#\n")
    #
    # Write "social=" entries
    #
    output.write (social.replace("NAME",name))
    nosocial = True
    for link in links:
        if link != "":
            output.write ("social=" + link + "\n")
            nosocial = False
    if nosocial:
        output.write ("# social=\n")
    #
    # Write "vendor=" entry
    #
    output.write (vndr.replace("NAME",name))
    if vendor != "":
        output.write ("vendor=" + vendor + "\n")
    else:
        output.write ("# vendor=\n")
    #
    # Write "contact=" entry
    #
    output.write (cntct.replace("NAME",name))
    if contact != "":
        output.write ("contact=" + contact + "\n")
    else:
        output.write ("# contact=\n")
    #
    # Write copyright if present
    #
    if copyright != "":
        output.write ("#\n# " + copyright + "\n")
#
# findurl (string,soup) - Find "href=" followed by a URL containing str in HTML soup, return url or "" if none found.
#
def findurl(string,soup):
    global href
    #
    # Find all occurances of "href=" followed by a url containing string
    #
    tags = soup.find_all(href=re.compile(string))
    #
    if (verbose):
        print ("findurl:string = ", string, "tags =", tags)
    #
    href = ""
    if len(tags) > 0:
        #
        # Check each occurance for a valid match
        #
        for tag in tags:
            #
            # Parse HTML for this tag and get url from href
            #
            url = html.unescape(str(tag))
            parser = MyHTMLParser()
            parser.feed(url)
            url = href
            #
            if url.startswith("/click?url="):
                url = url[11:len(url)]
            #
            # Check for exception match or if the string is not in the found url, if so check next match
            #
            if string.endswith(".com"):
                teststr = string[0:len(string)-4]
            else:
                teststr = string
            #
            if url in exceptions or teststr not in url:
                url = ""
            else:
                #
                # Check for embedded exceptions, if not found return url, otherwise check next match
                #
                found = False
                for excptn in embedded:
                    if url.find(excptn) > 0:
                        found = True
                if not found:
                    break
                else:
                    url = ""
    else:
        url = ""
    #
    # Do final cleanup
    #
    if url != "":
        #
        # Strip after "?" or "#"
        #
        index = url.find("?")
        if index > 0:
            url = url[0:index]
        index = url.find("#")
        if index > 0:
            url = url[0:index]
        #
        # Prepend "https:" to url if missing
        #
        if url.startswith("//"):
            url = "https:" + url
        #
        # Don't unquote urls with "%2C" (commas), otherwise unquote them
        #
        if url.find("%2C") < 0:
            url = unquote(url)
    #
    if (verbose):
        print("findurl:url = ", url)
    #
    return (url)
#
# findcontact(soup) - Find contact URL in HTML soup, return url or "" if none found.
#
def findcontact(rurl,soup):
    #
    # Find contact link
    #
    for cntct in contactlist:
        contact = findurl(cntct,soup)
        if contact != "":
            #
            # If an absolute url prepend domain url
            #  
            if contact.startswith("/"):
                index1 = rurl.find("://") + 3
                index2 = rurl[index1:len(rurl)].find("/")
                baseurl = rurl[0:index1+index2]
                if baseurl.endswith("/"):
                    contact = baseurl + contact[1:len(contact)]
                else:
                    contact = baseurl + contact
            elif contact.startswith("./"):
                if url.endswith("/"):
                    contact = rurl + contact[2:len(contact)]
                else:
                    contact = rurl + contact[1:len(contact)]
            elif contact.startswith("#") or contact.startswith("a") or contact.startswith("c"):
                if url.endswith("/"):
                    contact = rurl + contact
                else:
                    contact = rurl + "/" + contact
            break
    return(contact)
#
# findtel (text) - Find telephone number in HTML text, return tel:<phone number>
#
def findtel(text):
    #
    # Find all occurances of xxx-xxx-xxxx or (xxx) xxx-xxxx
    #
    list = re.findall("[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]",text)
    if len(list) !=0:
        phone = "tel:" + list[0].strip()
    else:
        list = re.findall("\([0-9][0-9][0-9]\) [0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]",text)
        if len(list) !=0:
            phone = "tel:" + list[0].strip()
        else:
            phone = ""
    #
    if (verbose):
        print("findtel:phone = ", phone)
    #
    return(phone)
#
# findcopyright (text) - Find copyright text in HTML text, return copyright string
# 
# Obsserved Copyright forms:
# 1.	"copyright [0-9]{4}"
# 2.    "copyright © [0-9]{4}"
# 3.    "copyright ©[0-9]{4}"
# 4.    "copyright ©"
# 4.    "copyright (c) [0-9]{4}"
# 5.    "© [0-9]{4}"
# 6.    "©[0-9]{4}"
# 7.    "© copyright"
# 8.    "©"
#
def findcopyright(text):
    #
    # Define various forms of "copyright"
    #
    copyrightlist = ["copyright [0-9]{4}", "copyright © [0-9]{4}", "copyright ©[0-9]{4}", "copyright ©", "copyright (c) [0-9]{4}", "© [0-9]{4}", "©[0-9]{4}", "© copyright", "©"]
    #
    # Initialize variables
    #
    copyright = ""
    #
    # Remove newlines, some unnecessary characters (&not; &dagger;), comments, scripts, and embedded links
    #
    text = re.sub(re.compile("[¬|†|\n|\r|]")," ",text)
    text = re.sub(re.compile("<!--[^-]*-->"),"",text)
    text = re.sub(re.compile("/\* [^\*]*\*/"),"",text)
    text = re.sub(re.compile("<script>[^>]*</script>"),"",text)
    text = re.sub(re.compile("<a [^>]*>"),"",text)
    #
    # Step through copyright list to check its various forms
    #
    for string in copyrightlist:
        #
        if (verbose):
            print ("findcopyright:string = ", string)
        #
        list = re.findall(re.compile(">[^>]*" + string + "[^<]*<",re.IGNORECASE),text)
        #
        if (verbose):
            print ("findcopyright:list = ", list)
        #
        for copyright in list:
            #
            # If match has an "http" link or "-copyright" or "SiteCatalyst", check next match
            #
            if copyright.find("http") < 0 and copyright.find("-copyright") < 0 and copyright.find("SiteCatalyst") < 0:
                #
                # Check for "<meta name=\"copyright\" content=" and remove it
                #
                if copyright.find("<meta name=\"copyright\" content=") >= 0:
                    copyright = copyright.replace("<meta name=\"copyright\" content=","")
                    copyright = copyright.replace("/>","")
                    copyright = copyright.replace("\"","")
                #
                # Check for "<meta name=\"rights\" content=" and remove it
                #
                if copyright.find("<meta name=\"rights\" content=") >= 0:
                    copyright = copyright.replace("<meta name=\"rights\" content=","")
                    copyright = copyright.replace("/>","")
                    copyright = copyright.replace("\"","")
                #
                # Remove leading ">" and trailing "<", strip extraneous spaces
                #
                copyright = copyright[1:len(copyright)-1]
                copyright = copyright.strip()
                copyright = re.sub("\s+"," ",copyright)
                #
                break
            else:
                copyright = ""
        if copyright != "":
            break
    #
    if (verbose):
        print ("findcopyright:copyright =", copyright)
    # 
    return(copyright)
#
# trustfilename(url) - generate a trust.txt filename from url
#
def trustfilename(url,dirname):
    #
    # Create output trust.txt filename from url
    #
    index = url.find("://")
    domain = url[index+3:len(url)]
    filename = domain.replace("/","-")
    if (filename.endswith("-")):
        filename = dirname + "/" + filename + "trust.txt"
    else:
        filename = dirname + "/" + filename + "-trust.txt"
    return (filename)
#
# htmlfilenam(url) - generate an filename from url
#
def htmlfilename(url,dirname):
    #
    # Create output HTML filename from url
    #
    index = url.find("://")
    domain = url[index+3:len(url)]
    filename = domain.replace("/","-")
    if (filename.endswith("-")):
        filename = dirname + "/" + filename[0:len(filename)-1] + ".html"
    else:
        filename = dirname + "/" + filename + ".html"
    return (filename)
#
# readurl(url) - Reads the content of the specified url
# 
# Returns success (True or False), exception (True or False), the request response, and error string.
# 
# Valid success & exception states (cannot have both success = True and exception = True):
#
#    success = True,  exception = False - trust.txt file found
#    success = False, exception = True  - connection error occured trying to connect to site
#
def readurl(url,dirname):
    #
    if (verbose):
        print ("readurl:url =", url, "dirname = ", dirname)
    # 
    # Get HTML filename
    #
    filename = htmlfilename(url,dirname)
    #
    if os.path.isfile(filename):
        success = True
        error = ""
        #
        # Open HTML file and read contents
        #
        file = open(filename,"r")
        text = file.read()
        file.close()
    else:
        success = False
        error = "file: ", filename, "not found"
        text = ""
    #
    # Return results
    #
    return success, text, error  
#
# process(url) - Process the given url to find all the social, contact, and vendor links
#
def process (url,dirname):
    #
    if (verbose):
        print ("process:url = ", url)
    #
    rurl = url
    text = ""
    name = ""
    contact = ""
    links = []
    vendor = ""
    copyright = ""
    cntrl = ""
    cntrldby = ""
    #
    # If redo, read contents of HTML file previously saved, Fetch home page
    #
    if redo:
        success, text, error = readurl(url,dirname)
        exception = False
    else:
        success, exception, r, error = fetchurl(url)
        if success:
            rurl = r.url
            text = r.text
    #
    # If successful, find links
    #
    if success:
        #
        # Save file if -s option used
        #
        if save:
            #
            # If save HTML, create output filename from url, prepend dirname, and write response
            #
            filename = htmlfilename(rurl,dirname)
            file = open(filename,"w")
            file.write(r.text)
            file.close()
        #
        skip = False
        #
        # Remove text after "?" or "#" from returned url
        #
        index = rurl.find("?")
        if index > 0:
            rurl = rurl[0:index-1]
        index = rurl.find("#")
        if index > 0:
            rurl = rurl[0:index-1]
        name = ""
        contact = ""
        vendor = ""
        copyright = ""
        cntrl = ""
        cntrldby = ""
        #
        # Check for errors
        #
        for error in errors:
            if (text.find(error) >= 0):
                skip = True
                print ("Error for ", url, ":", error)
                break
        #
        # Check for domain registrar redirects
        #
        for registrar in registrars:
            if (rurl.find(registrar) >= 0):
                skip = True
                print ("Redirect ", url, " to domain registrar: ", registrar)
                break
        #
        if not skip:
            #
            # Unescape HTML escaped characters
            #
            untext = html.unescape(text)
            soup = BeautifulSoup(untext)
            #
            # Get title, strip "<title>" and "</title>" to get name
            #
            name = html.unescape(str(soup.title))
            #
            name = re.sub("<title[^>]*>","",name,1)
            name = name.replace("</title>","")
            name = name.replace("\n","")
            name = name.replace("\r","")
            name = name.replace(","," ")
            #
            # Remove home page designation from name
            #
            for home in homepage:
                name = re.sub(re.compile(home,re.IGNORECASE),"",name)
            #
            # Strip leading and trailing spaces
            #
            name = name.strip()
            #
            if verbose:
                print ("name = ", name)
            #
            # Find contact link
            #
            contact = findcontact(rurl,soup)
            #
            # If not found, look for a telephone number
            #
            if contact == "":
                contact = findtel(untext)
            #
            if verbose:
                print ("contact = ", contact)
            #
            # Find social network links
            #
            links = []
            for social in socials:
                socialurl = findurl(social,soup)
                #
                # If not found try removing ".com" and prepending "/"
                #
                if socialurl == "":
                    social = "/" + social[0:len(social)-4]
                    socialurl = findurl(social,soup)
                    #
                    # If found starting with "/" prepend baseurl
                    #
                    if socialurl.startswith("/"):
                        index1 = rurl.find("://") + 3
                        index2 = rurl[index1:len(rurl)].find("/")
                        baseurl = rurl[0:index1+index2]
                        if baseurl.endswith("/"):
                            socialurl = baseurl + socialurl[1:len(socialurl)]
                        else:
                            socialurl = baseurl + socialurl
                links.append(socialurl)
            #
            if verbose:
                print ("links = ", links)
            #
            # Find if there is a vendor link
            #
            vendor = ""
            for link in vendors:
                if (untext.find(link) >= 0):
                    vendor = "https://www." + link + "/"
                    break
            #
            if verbose:
                print ("vendor = ", vendor)
            #
            # Find Copyright
            #
            copyright = findcopyright(untext).replace(","," ")
            #
            if verbose:
                print ("vendor = ", vendor)
            #
            # Check if copyright contains a chain
            #
            cntrldby = ""
            for chain in chains.keys():
                if (copyright.find(chain) >= 0):
                    cntrldby = chains[chain]
            #
            if verbose:
                print ("cntrldby = ", cntrldby)
    else:
        skip = True
        rurl = url
        name = ""
        contact = ""
        links = []
        vendor = ""
        copyright = ""
        cntrl = ""
        cntrldby = ""
        if exception:
            copyright = error.replace(","," ")
    #
    if (verbose):
        print ("process:rurl = ", rurl, "name = ", name, "contact= ", contact, "links = ", links, "vendor = ", vendor, "copyright = ", copyright, "cntrl = ", cntrl, "cntrldby = ", cntrldby, "skip = ", skip)
    #
    return rurl, name, contact, links, vendor, copyright, cntrl, cntrldby, skip
#
# chkecosys (url, ecosys) - Check for url in ecosystem, if present return attributes discovered
#
def chkecosys (url, ecosys):
    #
    # Initialize variables
    #
    contact = ""
    links = []
    vendor = ""
    controls = []
    controlledby = ""
    members = []
    belongtos = []
    domain = url[url.find("://")+3:len(url)]
    #
    if verbose:
        print ("chkecosys:domain = ", domain)
    #
    for entry in ecosys:
        #
        # Split entry into srcurl, attr, refurl
        #
        entry = entry.strip("\n")
        temp = entry.split(",",2)
        #
        srcurl = temp[0]
        attr = temp[1]
        refurl = temp[2]
        #
        # Check if domain is in the srcurl
        #
        if srcurl.find(domain) > 0:
            #
            # If this is a srcurl, then capture attributes of existing trust.txt file
            #
            if attr == "belongto" and refurl not in belongtos:
                belongtos.append(refurl)
            elif attr == "member" and refurl not in members:
                members.append(refurl)
            elif attr == "social" and refurl not in links:
                links.append(refurl)
            elif attr == "contact":
                contact = refurl
            elif attr == "control" and refurl not in controls:
                controls.append(refurl)
            elif attr == "controlledby":
                controlledby = refurl
            elif attr == "vendor":
                vendor = refurl
        #
        # Check if url is the refurl in a member entry in the ecosystem, if so append the srcurl to the belongtos list if not already present
        #
        if refurl.find(domain) > 0 and attr == "member" and srcurl not in belongtos:
            belongtos.append(srcurl)
    if verbose:
        print ("contact = ", contact, "links = ", links, "vendor", vendor, "control = ", controls, "controlledby = ", controlledby, "members = ", members, "belongtos = ", belongtos)
    #
    return contact, links, vendor, controls, controlledby, members, belongtos
#
# Main program
#
# Ignore warnings
#
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
#
# Create argument parser
#
parser = argparse.ArgumentParser(description="Scrapes websites to discover: 'name', 'contact', 'social', and 'copyright' and writes trust.txt file. Optionally, checks webcrawler ouptut for additional 'belongto' entries.")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-s", "--save", help="save HTML from the website", action="store_true")
parser.add_argument("-r", "--redo", help="redo generation of trust.txt files from HTML previously saved with -s option", action="store_true")
parser.add_argument("-j", "--forcejl", help="force belongto=https://www.journallist.net/", action="store_true")
parser.add_argument("-d", "--dirname", help="name of directory to write output, defualt to current directory", type=str, action="store")
parser.add_argument("-w", "--webcrawl", help="name of webcrawler output directory to check for belongto entries", type=str, action="store")
parser.add_argument("url_or_filename", help="url to scrape or name of a .csv file containing a list of urls to scape", type=str, action="store")
#
# Parse arguments
#
args = parser.parse_args()
#
verbose = args.verbose
redo = args.redo
if redo:
    save = False
else:
    save = args.save
forcejl = args.forcejl
dirname = str(args.dirname)
webcrawl = str(args.webcrawl)
url_or_filename = str(args.url_or_filename)
#
if (verbose):
    print ("args = ", args)
#
ecosyschk = False
lines = []
ecosys = []
members = []
belongtos = []
#
# If the parameter does not begin with "http" and ends with ".csv", then read list of urls from file.
#
if not url_or_filename.startswith("http") and url_or_filename.endswith(".csv"):
    csv = True
    #
    # Open .csv file file and read list of urls
    #
    infile = open(url_or_filename,encoding="utf-8-sig")
    lines = infile.readlines()
    infile.close()
else:
    csv = False
    #
    # Set lines to the url provided
    #
    lines.append(url_or_filename)
#
# If an output directory name is provided, check if it exists and create if necessary. Otherwise, set dirname to "."
#
if dirname != "None":
    if not os.path.isdir(dirname):
        #
        # Create output directory
        #
        os.mkdir(dirname)
else:
    dirname = "."
#
# If webcrawl directory name is provided, check if webcrawl output file exists, open it, read the contents, and close it
#
filename = ""
if (webcrawl != "None"):
    filename = webcrawl + "/" + webcrawl + ".csv"
    if os.path.isfile(filename):
        ecosyschk = True
        crawlfile = open(filename, "r")
        ecosys = crawlfile.readlines()
        crawlfile.close()
    else:
        ecosyschk = False
        print (filename, " not found, skipping belongto checks")
#
# If processing a list of urls, create an output.csv file and write header.
#
if csv:
    if dirname != ".":
        csvfile = open(dirname + "/" + dirname + "-output.csv", "w")
    else:
        csvfile = open(dirname + "/output.csv", "w")
    #
    csvfile.write ("Name,Website,Contact,")
    for social in socials:
        csvfile.write (social + ",")
    csvfile.write ("Vendor,Copyright,Controlledby,Belongto\n")
#
# Process each url
#
for url in lines:
    #
    url = url.strip("\n")
    if url.startswith("http"):
        #
        if verbose:
            print ("Processing: ", url)
        #
        rurl, name, contact, links, vendor, copyright, cntrl, cntrldby, skip = process(url,dirname)
        #
        if not skip:
            #
            # Create output trust.txt filename from url and prepend dirname.
            #
            filename = trustfilename(rurl,dirname)
            #
            if verbose:
                print ("Filename = ", filename)
            #
            # If ecosystem check enabled, check ecosystem for entries for this url
            #
            if ecosyschk:
                contact, links, vendor, controls, cntrldby, members, belongtos = chkecosys (rurl, ecosys)
            #
            # If force belongto journallist.net append it to the belongtos list if not already present
            #
            if forcejl and "journallist.net" not in belongtos:
                belongtos.append("https://www.journallist.net/")
            #
            # Open trust.txt file, write contents, and close it.
            #
            trustfile = open(filename, "w")
            write_trust_txt(name, rurl, contact, links, vendor, copyright, controls, cntrldby, members, belongtos, trustfile)
            trustfile.close()
            #
            # If processing a list of urls, write to output.csv file
            #
            if csv:
                csvfile.write (name + "," + rurl + "," + contact)
                #
                # Write socials
                #
                for link in links:
                    csvfile.write ("," + link)
                csvfile.write ("," + vendor + "," + copyright + "," + cntrldby)
                #
                # Write belongtos
                #
                for blng in belongtos:
                    csvfile.write ("," + blng)
                #
                csvfile.write ("\n")
#
# Close output.csv file if necessary
#
if csv:
    csvfile.close()