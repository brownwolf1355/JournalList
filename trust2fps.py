#!/usr/local/bin/python3.10
#
import sys
import os
from urllib.parse import urlparse
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
# Read the trust.txt file, remove whitespace and return a list of referenced domains in "control=" entries and the "contact=" reference, remove any references that are the same as primary
#
def readtrust (filename, primary):
    #
    # Open file, read contents, and process each line
    #
    file = open(filename,"r")
    lines = file.readlines()
    list = []
    contact = ""
    for line in lines:
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
        # Extract attribute and referenced url
        #
        attr = tmpline.split("=",2)
        if (len(attr) == 2) and (attr[1] != ""):
            if (attr[0] == "control"):
                #
                # Normalize the referenced url
                #
                domain, subdomain, subdir = normalize(attr[1])
                #
                # If not equal to primary append domain to list
                #
                if (domain != primary):
                    list.append(domain)
            elif (attr[0] == "contact"):
                #
                # Set contact
                #
                contact = attr[1]
    #
    # Close file and return list
    #
    file.close()
    return list, contact
#
# Write first_party_set.json to filepath using primary domain, list of domains and contact
#
def writefps (filename, primary, list, contact):
    #
    # Open output file
    #
    file = open(filename,"w")
    #
    # Write contact and primary entries
    #
    file.write("{\n  \"sets\": [\n    {\n      \"contact\": \"" + contact + "\",\n      \"primary\": \"https://" + primary + "\",\n\n")
    #
    # Write associatedSites list
    #
    file.write("      \"associatedSites\": [\"")
    lenlist = len(list)
    if lenlist == 2:
        file.write("https://" + list[0] + "\", \"")
    else:
        for i in range(0,lenlist-2):
            file.write("https://" + list[i] + "\", \"")
    file.write("https://" + list[lenlist-1] + "\"],\n\n")
    #
    # Write rationaleBySite list
    #
    file.write("      \"rationaleBySite\": {\n")
    if lenlist == 2:
        file.write("        \"" + "https://" + list[0] + "\": \"Through common branding and/or common copyright and/or listed as associated brands on primary site\",\n")
    else:
        for i in range(0,lenlist-2):
            file.write("        \"" + "https://" + list[i] + "\": \"Through common branding and/or common copyright and/or listed as associated brands on primary site\",\n")
    file.write("        \"" + "https://" + list[lenlist-1] + "\": \"Through common branding and/or common copyright and/or listed as associated brands on primary site\"\n")
    #
    # Write closing json text
    #
    file.write("      }\n    }\n  ]\n}\n")
    return
#
# Write associateSite first_party_set.json to filepath using primary domain
#
def writeassoc (filename, primary):
    #
    # Open output file
    #
    file = open(filename,"w")
    #
    # Write primary entry
    #
    file.write("{\n  \"primary\": \"https://" + primary + "\"\n}\n")
#
# Main program
#
if len(sys.argv) > 1:
    filepath = sys.argv[1]
    #
    # Check if file exists
    #
    if (os.path.isfile(filepath)):
        #
        # Filename should be of the form "wwww.<domain>-trust.txt"
        #
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)
        fpspath = filepath.replace("trust.txt","first_party_sets.json")
        domain = filename.replace("www.","")
        domain = domain.replace("-trust.txt","")
        #
        list, contact = readtrust (filepath, domain)
        #
        # If there are "control=" entries, then write the first_party_set.json file, else print error
        #
        if (len(list) != 0):
            writefps (fpspath, domain, list, contact)
            assocpath = "associateSite-first_party_sets.json"
            if (domain != ""):
                assocpath = dirname + "/" + assocpath
            #
            writeassoc (assocpath, domain)
        else:
            print ("No control entries in trust.txt file")
    else:
        print (filepath, " does not exist")
else:
    print ("no argument given")