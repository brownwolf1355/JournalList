#!/usr/local/bin/python3.10
#
# Parses the symmetric.csv file generated by the JournalList.net webcrawler to generate a .graphml social graph.
#
# Name - graphml.py
# Synopsis - graphml.py [DIRNAME]
#   DIRNAME - optional, the directory containing the symmetric.csv file. Default is "Webcrawl-YYYY-MM-DD" where "YYYY-MM-DD" is today's date.
#
# Copyright (c) 2021 Brown Wolf Consulting LLC
# License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import time
#
# Set global colors
#
green = "#00FF00"
lightgreen = "#90EE90"
blue = "#0000FF"
lightblue = "#87CEFA"
yellow = "#FFFF00"
lightyellow = "#FFFFE0"
red = "#FF0000"
black = "#000000"
white = "#FFFFFF"
#
# Write header to a gmlfile
# 
def write_header(gmlfile, title):
    #
    # Write graphml header to file
    #
    gmlfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    gmlfile.write("<graphml\n")
    gmlfile.write("  xmlns=\"http://graphml.graphdrawing.org/xmlns\"\n")
    gmlfile.write("  xmlns:java=\"http://www.yworks.com/xml/yfiles-common/1.0/java\"\n")
    gmlfile.write("  xmlns:sys=\"http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0\"\n")
    gmlfile.write("  xmlns:x=\"http://www.yworks.com/xml/yfiles-common/markup/2.0\"\n")
    gmlfile.write("  xmlns:xlink=\"http://www.w3.org/1999/xlink\"\n")
    gmlfile.write("  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
    gmlfile.write("  xmlns:y=\"http://www.yworks.com/xml/graphml\"\n")
    gmlfile.write("  xmlns:yed=\"http://www.yworks.com/xml/yed/3\"\n")
    gmlfile.write("  xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns graphml+xlink.xsd\">\n")
    gmlfile.write("  <key for=\"port\" id=\"d0\" yfiles.type=\"portgraphics\"/>\n")
    gmlfile.write("  <key for=\"port\" id=\"d1\" yfiles.type=\"portgeometry\"/>\n")
    gmlfile.write("  <key for=\"port\" id=\"d2\" yfiles.type=\"portuserdata\"/>\n")
    gmlfile.write("  <key attr.name=\"url\" attr.type=\"string\" for=\"node\" id=\"d3\"/>\n")
    gmlfile.write("  <key attr.name=\"description\" attr.type=\"string\" for=\"node\" id=\"d4\"/>\n")
    gmlfile.write("  <key for=\"node\" id=\"d5\" yfiles.type=\"nodegraphics\"/>\n")
    gmlfile.write("  <key for=\"node\" id=\"d6\" yfiles.type=\"nodegraphics\"/>\n")
    gmlfile.write("  <key for=\"graphml\" id=\"d7\" yfiles.type=\"resources\"/>\n")
    gmlfile.write("  <key attr.name=\"url\" attr.type=\"string\" for=\"edge\" id=\"d8\"/>\n")
    gmlfile.write("  <key attr.name=\"description\" attr.type=\"string\" for=\"edge\" id=\"d9\"/>\n")
    gmlfile.write("  <key for=\"edge\" id=\"d10\" yfiles.type=\"edgegraphics\"/>\n")
    gmlfile.write("\n")
    gmlfile.write("  <graph id=\"" + title + "\" edgedefault=\"directed\">\n")
#
# Write the tail of the gmlfile and close it.
#
def write_tail(gmlfile):
    gmlfile.write("  </graph>\n")
    gmlfile.write("  <data key=\"d6\">\n")
    gmlfile.write("    <y:Resources/>\n")
    gmlfile.write("  </data>\n")
    gmlfile.write("</graphml>\n")
#
# Write a node definition to the gmlfile.
#
def write_node (gmlfile, url, color, border):
    #
    # Set href to the url's trust.txt file, unless the node color is lightgreen, lightblue, or lightyellow, in which case set href to "https://www.journallist.net/missing_trust_file/"
    #
    href = url + "trust.txt"
    if (color == lightgreen or color == lightblue or color == lightyellow):
        href = "https://www.journallist.net/missing_trust_file/"
    #
    nodeid = url[8:len(url)-1]
    #
    # If node id is "www.publisher.com" or "www.association.com" or "www.vendor.com" or "missing_trust.txt_file" then set href to "https://www.journallist.net/definitions/"
    #
    if (nodeid == "www.publisher.com" or nodeid == "www.association.com" or nodeid == "www.vendor.com" or nodeid == "missing_trust.txt_file" ):
        href = "https://www.journallist.net/definitions/"
    #
    # print ("url =", url, "nodeid =", nodeid, "color =", color, "href =", href)
    #
    gmlfile.write("    <node id=\"" + nodeid + "\" xlink:href=\"" + href + "\">\n")
    gmlfile.write("      <data key=\"d3\" xml:space=\"preserve\"><![CDATA[" + href + "]]></data>\n")
    gmlfile.write("      <data key=\"d4\" xml:space=\"preserve\"><![CDATA[" + nodeid + "]]></data>\n")
    gmlfile.write("      <data key=\"d5\">\n")
    gmlfile.write("        <y:ShapeNode>\n")
    gmlfile.write("          <y:Fill color=\"" + color + "\" transparent=\"false\"/>\n")
    gmlfile.write("          <y:BorderStyle color=\"#000000\" type=\"" + border + "\" width=\"1.0\"/>\n")
    gmlfile.write("          <y:NodeLabel modelName=\"sides\" modelPosition=\"e\">" + nodeid + "</y:NodeLabel>\n")
    gmlfile.write("          <y:Shape type=\"ellipse\"/>\n")
    gmlfile.write("        </y:ShapeNode>\n")
    gmlfile.write("      </data>\n")
    gmlfile.write("    </node>\n")
#
# Write a bidirectional edge definition to the gmlfile.
#
def write_biedge (gmlfile, source, target, forward, backward):
    sourceid = source[8:len(source)-1]
    targetid = target[8:len(target)-1]
    #
    # Write forward edge
    #
    gmlfile.write("    <edge source=\"" + sourceid + "\" target=\"" + targetid + "\">\n")
    gmlfile.write("      <data key=\"d9\"/>\n")
    gmlfile.write("      <data key=\"d10\">\n")
    gmlfile.write("        <y:LineEdge>\n")
    gmlfile.write("          <y:LineStyle color=\"#000000\" type=\"line\" width=\"1.0\"/>\n")
    gmlfile.write("          <y:EdgeLabel fontSize=\"9\" backgroundColor=\"#FFFFFF\" modelName=\"custom\" preferredPlacement=\"anywhere\">" + forward + "<y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\"/>\n")
    gmlfile.write("          <y:LabelModel><y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\" candidateMask=\"128\" distance=\"2.0\" positionRelativeToSegment=\"false\"/></y:LabelModel><y:ModelParameter><y:RotatedDiscreteEdgeLabelModelParameter position=\"scenter\"/></y:ModelParameter>\n")
    gmlfile.write("          </y:EdgeLabel>\n")
    gmlfile.write("        </y:LineEdge>\n")
    gmlfile.write("      </data>\n")
    gmlfile.write("    </edge>\n")
    #
    # Write backward edge
    #
    gmlfile.write("    <edge source=\"" + targetid + "\" target=\"" + sourceid + "\">\n")
    gmlfile.write("      <data key=\"d9\"/>\n")
    gmlfile.write("      <data key=\"d10\">\n")
    gmlfile.write("        <y:LineEdge>\n")
    gmlfile.write("        <y:LineStyle color=\"#000000\" type=\"line\" width=\"1.0\"/>\n")
    gmlfile.write("          <y:EdgeLabel fontSize=\"9\" backgroundColor=\"#FFFFFF\" modelName=\"custom\" preferredPlacement=\"anywhere\">" + backward + "<y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\"/>\n")
    gmlfile.write("          <y:LabelModel><y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\" candidateMask=\"128\" distance=\"2.0\" positionRelativeToSegment=\"false\"/></y:LabelModel><y:ModelParameter><y:RotatedDiscreteEdgeLabelModelParameter position=\"scenter\"/></y:ModelParameter>\n")
    gmlfile.write("          </y:EdgeLabel>\n")
    gmlfile.write("        </y:LineEdge>\n")
    gmlfile.write("      </data>\n")
    gmlfile.write("    </edge>\n")
#
# Write a unidirectional edge definition to the gmlfile.
#
def write_uniedge (gmlfile, source, target, forward):
    sourceid = source[8:len(source)-1]
    targetid = target[8:len(target)-1]
    gmlfile.write("    <edge source=\"" + sourceid + "\" target=\"" + targetid + "\">\n")
    gmlfile.write("      <data key=\"d7\"/>\n")
    gmlfile.write("      <data key=\"d10\">\n")
    gmlfile.write("        <y:LineEdge>\n")
    gmlfile.write("          <y:LineStyle color=\"#000000\" type=\"line\" width=\"1.0\"/>\n")
    gmlfile.write("          <y:EdgeLabel fontSize=\"9\" backgroundColor=\"#FFFFFF\" modelName=\"custom\" preferredPlacement=\"anywhere\">" + forward + "<y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\"/>\n")
    gmlfile.write("          <y:LabelModel><y:RotatedDiscreteEdgeLabelModel angle=\"0.0\" autoRotationEnabled=\"true\" candidateMask=\"128\" distance=\"2.0\" positionRelativeToSegment=\"false\"/></y:LabelModel><y:ModelParameter><y:RotatedDiscreteEdgeLabelModelParameter position=\"scenter\"/></y:ModelParameter>\n")
    gmlfile.write("          </y:EdgeLabel>\n")
    gmlfile.write("        </y:LineEdge>")
    gmlfile.write("      </data>\n")
    gmlfile.write("    </edge>\n")
#
# Write graphml ledgend.
#
def write_legend(gmlfile):
    #
    # Write legend nodes and edges (no need for missing_trust.txt_file in symmetric version)
    #
    write_node(gmlfile,"https://www.association.com/",green,"line")
    write_node(gmlfile,"https://www.publisher.com/",blue,"line")
    write_node(gmlfile,"https://www.vendor.com/",yellow,"line")
    write_node(gmlfile,"https://missing_trust.txt_file/",lightblue,"dashed")
    write_biedge(gmlfile,"https://www.association.com/","https://www.publisher.com/","member","belongto")
    write_biedge(gmlfile,"https://www.publisher.com/","https://www.vendor.com/","vendor", "customer")
    write_uniedge(gmlfile,"https://www.publisher.com/","https://missing_trust.txt_file/","control")
#
# Read a list of urls from associations, publishers, or vendors from a file and return list.
#
def readlist (filename):
    file = open(filename,"r")
    lines = file.readlines()
    list = []
    for line in lines:
        if (line not in list):
            list.append(line.rstrip())
    file.close()
    return list
#
# Set edge labels based on attr.
#
def edgelabels (attr):
#
# Set edge labels.
#
    forward = attr
    if (attr == "member"):
        backward = "belongto"
    elif (attr == "belongto"):
        backward = "member"
    elif (attr == "control"):
        backward = "controlledby"
    elif (attr == "controlledby"):
        backward = "control"
    elif (attr == "vendor"):
        backward = "customer"
    elif (attr == "customer"):
        backward = "vendor"
    #
    return (forward, backward)
#
# Set node color based on url's presence in the lists and the flag indicating presence of trust.txt file.
#
#  - Association = Green or light green if no trust.txt
#  - Publisher = Blue or light blue if no trust.txt
#  - Vendor = Yellow or light yellow if no trust.txt
#  - Controlled = Dashed border
#
def nodecolor (url, associations, publishers, vendors, controlled, trustfiles):
    #
    # Determine node color.
    #
    if (url in associations):
        if url in trustfiles:
            color = green
        else:
            color = lightgreen
    elif (url in publishers):
        if url in trustfiles:
            color = blue
        else:
            color = lightblue
    elif (url in vendors):
        if url in trustfiles:
            color = yellow
        else:
            color = lightyellow
    else:
        color = white
    #
    # Determine border type.
    #
    if (url in controlled):
        border = "dashed"
    else:
        border = "line"
    #
    return color, border
#
# matchsym (link, symmetric)
#
def matchsym (line, symmetric):
    #
    # Add the reverse direction to the line.
    #
    # print ("line = ", line)
    temp = line.split(",",2)
    srcurl = temp[0].strip()
    attr = temp[1].strip()
    refurl = temp[2].strip()
    #
    if (attr == "member"):
        temp = line + "," + refurl + ",belongto," + srcurl
    elif (attr == "belongto"):
        temp = line + "," + refurl + ",member," + srcurl
    elif (attr == "control"):
        temp = line + "," + refurl + ",controlledby," + srcurl
    elif (attr == "controlledby"):
        temp = line + "," + refurl + ",control," + srcurl
    elif (attr == "vendor"):
        temp = line + "," + refurl + ",customer," + srcurl
    elif (attr == "customer"):
        temp = line + "," + refurl + ",vendor," + srcurl
    try:
        index = symmetric.index(temp)
    except:
        match = False
    else:
        match = True
    return match       
#     
# Main program
#
# Specify symmetric and asymmetric attributes.
#
symattr = "member,belongto,control,controlledby,vendor,customer"
asymattr = "social,contact,disclosure"
#
# Set DIRNAME
#
if len(sys.argv) > 1:
    dirname = sys.argv[1]
else:
    dirname = "Webcrawl-"+time.strftime("%Y-%m-%d")
#
# Check if directory exists.
#
if (os.path.isdir(dirname)):
    #
    # Check if .csv file exists.
    #
    csvname = dirname + "/" + dirname + ".csv"
    if(os.path.isfile(csvname)):
        #
        # Derive filenames.
        #
        gmlname = dirname + "/" + dirname + ".graphml"
        symname = dirname + "/" + dirname + "-symmetric.graphml"
        asymname = dirname + "/" + dirname + "-asymmetric.graphml"
        symcsvname = dirname + "/" + dirname + "-symmetric.csv"
        assocname = dirname + "/" + dirname + "-associations.csv"
        pubname = dirname + "/" + dirname + "-publishers.csv"
        vendname = dirname + "/" + dirname + "-vendors.csv"
        ctrldname = dirname + "/" + dirname + "-controlled.csv"
        backname = dirname + "/" + dirname + "-back.csv"
        #
        # Read list of associations, publishers, and vendors, along with the list of those that they control.
        #
        associations = readlist(assocname)
        publishers = readlist(pubname)
        vendors = readlist(vendname)
        controlled = readlist(ctrldname)
        symmetric = readlist(symcsvname)
        #
        # Set the node and edge counts. Create an empty nodelist.
        #
        nodelist = []
        symnodes = []
        asymnodes = []
        #
        # Open the graphml output files.
        #
        symfile = open(symname,"w")
        asymfile = open(asymname,"w")
        gmlfile = open(gmlname,"w")
        #
        # Write graphml header to output files
        #
        write_header(gmlfile, "JournalList Ecosystem Graph - All Links")
        write_header(symfile, "JournalList Ecosystem Graph - Symmetric Links Only")
        write_header(asymfile, "JournalList Ecosystem Graph - Asymmetric Links Only")
        #
        # Write legend nodes and edges.
        #
        write_legend(gmlfile)
        write_legend(symfile)
        write_legend(asymfile)
        #
        # Read in the .csv file.
        #
        lines = readlist(csvname)
        #
        # Generate list of urls with trust.txt files (srcurl)
        #
        trustfiles = []
        for line in lines:
            #
            # Split line into srcurl, attr, and refurl
            #
            temp = line.split(",",2)
            srcurl = temp[0].strip()
            #
            # If scrurl not in the list of trust.txt files add it
            if (srcurl not in trustfiles):
                    trustfiles.append(srcurl)
        #
        # Check if a list of backward links exists, if so read it in and append it to lines in the .csv file.
        #
        if(os.path.isfile(backname)):
            backlines = readlist(backname)
            lines = lines + backlines
        #
        # Process each line in the symmetric.csv file.
        #
        for line in lines:
            #
            # Split line into srcurl, attr, and refurl
            #
            temp = line.split(",",2)
            srcurl = temp[0].strip()
            attr = temp[1].strip()
            refurl = temp[2].strip()
            #
            # Skip any nonsymmetric attribute
            #
            if (attr not in symattr):
                continue
            #
            # Determine edge labels.
            #
            forward, backward = edgelabels (attr)
            #
            # Check if link is in the symmetric list.
            #
            match = matchsym (line, symmetric)
            #
            # If match then write symmetric nodes and edges.
            #
            if match:
                #
                # Determine node colors and write node if necessary and bidirectional edge to gmlfile and symfile output files.
                #
                srccolor, srcborder = nodecolor (srcurl, associations, publishers, vendors, controlled, trustfiles)
                refcolor, refborder = nodecolor (refurl, associations, publishers, vendors, controlled, trustfiles)
                #
                if (srcurl not in nodelist):
                    nodelist.append(srcurl)
                    write_node (gmlfile, srcurl, srccolor, srcborder)
                if (refurl not in nodelist):
                    nodelist.append(refurl)
                    write_node (gmlfile, refurl, refcolor, refborder)
                if (srcurl not in symnodes):
                    symnodes.append(srcurl)
                    write_node (symfile, srcurl, srccolor, srcborder)
                if (refurl not in symnodes):
                    symnodes.append(refurl)
                    write_node (symfile, refurl, refcolor, refborder)
                #
                write_biedge (gmlfile, srcurl, refurl, forward, backward)
                write_biedge (symfile, srcurl, refurl, forward, backward)
            else:
                #
                # Check if this is the reverse of a symmetric link.
                #
                temp = line
                if (attr == "belongto"):
                    temp = refurl + ",member," + srcurl
                elif (attr == "controlledby"):
                    temp = refurl + ",control," + srcurl
                elif (attr == "customer"):
                    temp = refurl + ",vendor," + srcurl
                #
                match = matchsym (temp, symmetric)
                #
                if (not match):
                    #
                    # If not, determine node colors and write node if necessary and unidirectional edge to gmlfile and asymfile output files.
                    #
                    srccolor, srcborder = nodecolor (srcurl, associations, publishers, vendors, controlled, trustfiles)
                    refcolor, refborder = nodecolor (refurl, associations, publishers, vendors, controlled, trustfiles)
                    #
                    if (srcurl not in nodelist):
                        nodelist.append(srcurl)
                        write_node (gmlfile, srcurl, srccolor, srcborder)
                    if (refurl not in nodelist):
                        nodelist.append(refurl)
                        write_node (gmlfile, refurl, refcolor, refborder)
                    if (srcurl not in asymnodes):
                        asymnodes.append(srcurl)
                        write_node (asymfile, srcurl, srccolor, srcborder)
                    if (refurl not in asymnodes):
                        asymnodes.append(refurl)
                        write_node (asymfile, refurl, refcolor, refborder)
                    #
                    write_uniedge (gmlfile, srcurl, refurl, forward)
                    write_uniedge (asymfile, srcurl, refurl, forward)                
        #
        # Write the tail of the symfile and close it.
        #
        write_tail (symfile)
        write_tail (asymfile)
        write_tail (gmlfile)
        gmlfile.close()
        asymfile.close()
        symfile.close()
        #
    else:
        print (csvname, "doesn't exist")
else:
    print (dirname, "doesn't exist")