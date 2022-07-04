#!/usr/local/bin/python3.10
#
# JournalList.net website scraper to scan all sites in a list and find all social, contact, and vendor links.
#
# Name - sitescrape.py [input.csv output.csv | name website]
# Synopsis - sitescrape.py [input.csv output.csv | name website]
#   input.csv - a .csv file containing a list of sites to scan [Name, Website]
#   output.csv - the output .csv file containing [Website, Contact, Facebook, Instagram, Twitter, Youtube, LinkedIn, Vendor, Copyright, Control]
#   name - the name of the publication (same as Name in input.csv)
#   website - the URL of the website (same as Website in input.csv)
#
# Summary - This python script outputs a .csv list with [Website, Contact, Facebook, Instagram, Twitter, Youtube, LinkedIn, Vendor, Copyright, Control] 
#   if arguments are: input.csv  output.csv, otherwise it generates a trust.txt for the named website.
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import time
import requests
import re
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
    # Return results
    #
    return success, exception, r, error
#
# write_csv (website, contact, facebook, instagram, twitter, youtube, linkedin, vendor, copyright, control, csvfile) - Write the entry into the .csv file csvfile.
#
def write_csv (name, website, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, csvfile):
    csvfile.write (name + "," + website + "," + contact + "," + facebook + "," + instagram + "," + twitter + "," + youtube + "," + linkedin + "," + pinterest + "," + vendor + "," + copyright + "," + control + "\n")
#
# write_trust_txt (website, contact, facebook, instagram, twitter, youtube, linkedin, vendor, copyright, control, csvfile) - Write the entry into the .csv file csvfile.
#
def write_trust_txt (name, website, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, output):
    #
    # Define trust.txt file header and commment text
    #
    header = "# NAME trust.txt file\n#\n# For more information on trust.txt see:\n# 1. https://journallist.net - Home of the trust.txt specification\n# 2. https://datatracker.ietf.org/doc/html/rfc8615 - IETF RFC 8615 - Well-Known Uniform Resource Identifiers (URIs)\n# 3. https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml - IANA's list of registered Well-Known URIs\n#\n"
    contolledby = "# NAME s controlled by the following organization\n#\n"
    belongto = "#\n# NAME belongs to the following organizations\n#\nbelongto=https://journallist.net\n"
    social = "#\n# NAME social networks\n#\n"
    vndr = "#\n# NAME vendors\n#\n"
    cntct = "#\n# NAME contact info\n#\n"
    #
    # Write header
    #
    output.write (header.replace("NAME",name))
    #
    # If there is a controlling site, write the "controlledby="" entry
    #
    if control != "":
        output.write (contolledby.replace("NAME",name))
        output.write ("controlledby=" + control + "\n")
    #
    # Write "belongto="" entry
    #
    output.write (belongto.replace("NAME",name))
    #
    # Write "social=" entries
    #
    output.write (social.replace("NAME",name))
    nosocial = True
    if facebook != "":
        output.write ("social=" + facebook + "\n")
        nosocial = False
    if instagram != "":
        output.write ("social=" + instagram + "\n")
        nosocial = False
    if twitter != "":
        output.write ("social=" + twitter + "\n")
        nosocial = False
    if youtube != "":
        output.write ("social=" + youtube + "\n")
        nosocial = False
    if linkedin != "":
        output.write ("social=" + linkedin + "\n")
        nosocial = False
    if pinterest != "":
        output.write ("social=" + pinterest + "\n")
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
# findurl (str,text) - Find "href=" followed by a URL containing str in HTML text, return url or "" if none found.
#
def findurl(str,text):
    #
    # Define exceptions
    #
    exceptions = ["//staticxx.facebook.com","//staticxx.facebook.com/","http://facebook.com","https://facebook.com","//facebook.com","http://instagram.com","https://instagram.com","//instagram.com","http://twitter.com","https://twitter.com","//twitter.com","http://linkedin.com","https://linkedin.com","//linkedin.com","http://pinterest.com","https://pinterest.com","//pinterest.com"]
    #
    # Find all occurances of "href=" followed by str until closing ">"
    #
    # print ("str =", str)
    list = re.findall("href=[^ ]*" + str + "[^>]*>",text)
    # print ("list =", list)
    if len(list) !=0:
        #
        # Check each occurance for a valid match
        #
        for url in list:
            #
            # Remove single quotes, double quotes, and backslash characters
            #
            url = url.replace("'","")
            url = url.replace("\"","")
            url = url.replace("\\","")
            #
            # Remove leading "href="
            #
            url = url[5:len(url)]
            #
            # Remove text after an embedded " " and/or embedded "?" and/or embedded ">" and/or embedded "\n"
            #
            index = url.find(" ")
            if (index > 0):
                url = url[0:index]
            index = url.find("?")
            if (index > 0):
                url = url[0:index]
            index = url.find(">")
            if (index > 0):
                url = url[0:index]
            index = url.find("\n")
            if (index > 0):
                url = url[0:index]
            # print ("url = ", url)
            #
            # Check if url is "http:" or "https:" or str only, check next match
            #
            if (url == "https:") or (url == str):
                url = ""
                break
            #
            # Check for Word Press content ("wp-content"), share content ("share"), intent content ("/intent"), or ("appId") in url, if not found return url, otherwise check next match
            #
            index1 = url.find("/wp-content")
            index2 = url.find("share")
            index3 = url.find("/intent")
            index4 = url.find("appId")
            # print ("index1 = ", index1, "index2 = ", index2, "index3 = ", index3)
            if index1 < 0 and index2 < 0 and index3 < 0 and index4 < 0:
                break
            else:
                url = ""
        #
        # Check for exceptions
        #
        if url in exceptions:
            url = ""
    else:
        url = ""  
    return (url)
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
    return(phone)
#
# findcopyright (text) - Find copyright text in HTML text, return copyright string
#
def findcopyright(text):
    # print (text)
    #
    # Define various forms of "copyright"
    #
    copyrightlist = ["©", "\&copy;","Copyright", "\(c\)"]
    matchstr = "[a-z|A-Z|0-9|,|\.|\-|&|;|#| |\n]*"
    #
    # Find all occurances of copyright in its various forms
    #
    for str in copyrightlist:
        # print ("str = ", str, "len(str) = ", len(str))
        list = re.findall(str + matchstr,text)
        # print ("list = ", list)
        if len(list) !=0:
            temp = list[0].replace("\n","")
            if (str == "\(c\)"):
                index = 3
            elif (str == "\&copy;"):
                index = 6
            else:
                index = len(str)
            copyright = temp[index:len(temp)].strip("\n")
            break
        else:
            list = re.findall(matchstr + str,text)
            if len(list) !=0:
                temp = list[0].strip()
                if (str == "\(c\)"):
                    index = 3
                elif (str == "\&copy;"):
                    index = 6
                else:
                    index = len(str)
                copyright = temp[0:len(temp)-len(str)].strip("\n")
                break
            copyright = ""
    #
    # Replace "&amp;" with "&", "&#169;" with "©", and "&nbsp;" with " ", and "&quot;" with "\""
    #
    copyright = copyright.replace("&amp;","&")
    copyright = copyright.replace("&#169;","©")
    copyright = copyright.replace("&nbsp;"," ")
    copyright = copyright.replace("&quot;","\"")
    # 
    return(copyright)
    # 
    return(copyright)
#
# findcontact (text) - Find contact URL in HTML text, return URL string
#
def findcontact (text):
    #
    # Define various forms of "contact"
    #
    contactlist = ["contact-us", "Contact-Us", "ContactUs", "contactus", "Contact us", "contact us", "contact_us", "Contact", "contact", "CONTACT", "About Us", "about-us", "about", "mailto:"]
    #
    # Find contact link (try various forms in contactlist, then search for a phone number)
    #
    for str in contactlist:
        # print ("str =", str)
        contact = findurl (str, text)
        # print ("contact = ", contact)
        if (contact != ""):
            break
    if (contact == ""):
        contact = findtel (text)
    contact = contact.strip("'").replace(",", " ")
    #
    if (contact != ""):
        #
        # If a relative url prepend base url
        #  
        if contact.startswith("/"):
            if url.endswith("/"):
                contact = url + contact[1:len(contact)]
            else:
                contact = url + contact
        if contact.startswith("./"):
            if url.endswith("/"):
                contact = url + contact[2:len(contact)]
            else:
                contact = url + contact[1:len(contact)]
        if not contact.startswith("http") and not contact.startswith("mailto") and not contact.startswith("tel:"):
            contact = url + contact
    return(contact)
#
# process(html) - Process the given html to find all the social, contact, and vendor links.
#
def process (url):
    #
    # Define set of error text to check in returned HTML text
    #
    errors = ["Page Not Found", "Site Not Found", "Access denied", "Server Error"]
    #
    # Define list of domain registrars to check for expired domains
    #
    registrars = ["www.hugedomains.com", "www.domain.com", "www.godaddy.com", "www.namecheap.com", "www.name.com", "www.enom.com", "www.dynadot.com", "www.namesilo.com", "www.123-reg.co.uk", "www.bluehost.com"]
    #
    # Define list of known vendors
    #
    vendors = ["bulletlink.com", "creativecirclemedia.com", "dirxion.com", "going1up.com", "our-hometown.com", "townnews.com", "887media.com", "authentictexan.com", "crowct.com", 
"etypeservices.com", "etypeservices.net", "surfnewmedia.com", "websitesfornewspapers.com", "xyzscripts.com", "publishwithfoundation.com", "socastdigital.com",
"creativecirclemedia.com", "disqus.com", "locablepublishernetwork.com", "metropublisher.com"]
    #
    # Define media conglomerates that publish multiple brands on different domains
    #
    chains = {
        "C&S Media":"https://csmediatexas.com/",
        "CherryRoad Media":"https://cherryroad-media.com/",
        "Ellington":"http://www.connectionnewspapers.com/",
        "Gannett":"https://www.gannett.com/",
        "Hearst":"https://www.hearst.com/",
        "Lee Enterprises":"https://lee.net/",
        "Mountain Media":"https://mountainmedianews.com/"
        }
    #
    # Fetch home page
    #
    success, exception, r, error = fetchurl(url)
    #
    # If successful, find links
    #
    if (success):
        skip = False
        rurl = r.url
        contact = ""
        facebook = ""
        instagram = ""
        twitter = ""
        youtube = ""
        linkedin = ""
        pinterest = ""
        vendor = ""
        copyright = ""
        control = ""
        #
        # Check for errors
        #
        for error in errors:
            if (r.text.find(error) >= 0):
                skip = True
                print ("Error for ", url, ":", error)
                break
        #
        # Check for domain registrar redirects
        #
        for registrar in registrars:
            if (r.url.find(registrar) >= 0):
                skip = True
                print ("Redirect ", url, " to domain registrar: ", registrar)
                break
        if not skip:
            #
            # Find contact link
            #
            contact = findcontact (r.text)
            #
            # print ("contact = ", contact)
            #
            # Find Facebook link
            #
            facebook = findurl ("facebook.com", r.text)
            # print ("facebook = ", facebook)
            #
            # Find Instagram link
            #
            instagram = findurl ("instagram.com", r.text)
            # print ("instagram = ", instagram)
            #
            # Find Twitter link
            #
            twitter = findurl ("twitter.com", r.text)
            # print ("twitter = ", twitter)
            #
            # Find YouTube link
            #
            youtube = findurl ("youtube.com", r.text)
            # print ("youtube = ", youtube)
            #
            # Find LinkedIn link
            #
            linkedin = findurl ("linkedin.com", r.text)
            # print ("linkedin = ", linkedin)
            #
            # Find Pinterest link
            #
            pinterest = findurl ("pinterest.com", r.text)
            # print ("pinterest = ", pinterest)
            #
            # Find Vendor link
            #
            vendor = ""
            for name in vendors:
                if (r.text.find(name) >= 0):
                    vendor = "https://www." + name
                    break
            # print ("vendor = ", vendor)
            #
            # Find Copyright
            #
            copyright = findcopyright(r.text).replace(","," ")
            #
            # Check if copyright contains a chain
            #
            control = ""
            for chain in chains.keys():
                if (copyright.find(chain) >= 0):
                    control = chains[chain]
            # print ("control = ", control)
    else:
        skip = True
        rurl = url
        contact = ""
        facebook = ""
        instagram = ""
        twitter = ""
        youtube = ""
        linkedin = ""
        pinterest = ""
        vendor = ""
        copyright = ""
        control = ""
        if (exception):
            copyright = error.replace(","," ")
    return rurl, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, skip
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
if len(sys.argv) == 3:
    # print ("sys.argv = ", sys.argv)
    #
    # Determine if arguments are .csv files
    #
    if sys.argv[1].endswith(".csv") and sys.argv[2].endswith(".csv"):
        csv = True
        #
        # Open input.csv and output.csv files
        #
        infile = open(sys.argv[1],"r")
        outfile = open(sys.argv[2],"w")
        #
        # Write headers to output .csv file
        #
        write_csv ("Name of Paper", "Website", "Contact", "Facebook", "Instagram", "Twitter", "Youtube", "LinkedIn", "Pinterest", "Vendor", "copyright", "Control", outfile)
        #
        lines = infile.readlines()
        infile.close()
        count = 0
    else:
        csv = False
        lines = [sys.argv[1] + "," + sys.argv[2]]
        #
        # Create output trust.txt file name
        #
        filename = sys.argv[2]
        index = filename.find("://")
        filename = filename[index+3:len(filename)].replace("/","-")
        if (filename.endswith("-")):
            filename = filename + "trust.txt"
        else:
            filename = filename + "-trust.txt"
        #
        # Open output file
        #
        outfile = open(filename,"w")
        count = 1
    #
    # print ("csv = ", csv)
    # print ("lines = ", lines)
    for line in lines:
        # print ("line = ", line)
        tuple = line.split(",")
        # print ("tuple = ", tuple)
        #
        # Check if name provided
        #
        if len(tuple) == 2:
            name=tuple[0].strip()
            url=tuple[1].strip("\n")
        else:
            name="Publisher"
            url=tuple[0].strip("\n")
        #
        if (count != 0):
            print ("Processing: ", name, ", ", url)
            rurl, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, skip = process(url)
            if not skip:
                if csv:
                    write_csv (name, rurl, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, outfile)
                else:
                    write_trust_txt(name, rurl, contact, facebook, instagram, twitter, youtube, linkedin, pinterest, vendor, copyright, control, outfile)
        count = count + 1
    #
    outfile.close()
else:
    print ("usage: sitescrape.py [input.csv output.csv | name website]")