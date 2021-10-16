#!/usr/local/bin/python3.10
#
# Parses the symmetric.csv file generated by the JournalList.net webcrawler to generate a .graphml social graph.
#
# Name - graphml.py
# Synopsis - graphml.py [DIRNAME]
#   DIRNAME - optional, the directory containing the symmetric.csv file. Default is "Webcrawl-YYYY-MM-DD" where "YYYY-MM-DD" is today's date.
#
#--------------------------------------------------------------------------------------------------
import sys
import os
import time
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
def write_node (gmlfile, url, color):
    #
    nodeid = url[8:len(url)-1]
    gmlfile.write("    <node id=\"" + nodeid + "\" xlink:href=\"" + url + "trust.txt" + "\">\n")
    gmlfile.write("      <data key=\"d3\" xml:space=\"preserve\"><![CDATA[" + url + "trust.txt]]></data>\n")
    gmlfile.write("      <data key=\"d4\" xml:space=\"preserve\"><![CDATA[" + nodeid + "]]></data>\n")
    gmlfile.write("      <data key=\"d5\">\n")
    gmlfile.write("        <y:ShapeNode>\n")
    gmlfile.write("          <y:Fill color=\"" + color + "\" transparent=\"false\"/>\n")
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
# Main program
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
    # Set the node and edge counts. Create an empty nodelist.
    nodecout = 0
    edgecount = 0
    nodelist = []
    #
    # Set attribute colors. 
    #  - Association = Green
    #  - Publisher = Blue
    #  - Vendor = Yellow
    #  - No trust.txt = Red
    #
    association = "#00FF00"
    publisher = "#0000FF"
    vendor = "#FFFF00"
    control = "#0000FF"
    notrust = "#FF0000"
    #
    # Check if symmetric.csv file exists
    #
    csvname = dirname + "/" + dirname + "-symmetric.csv"
    if(os.path.isfile(csvname)):
        #
        # Read symmetric.csv file, process content and write to both full and symmetric graphml files.
        #
        gmlname = dirname + "/" + dirname + ".graphml"
        symname = dirname + "/" + dirname + "-symmetric.graphml"
        assocname = dirname + "/" + dirname + "-associations.csv"
        pubname = dirname + "/" + dirname + "-publishers.csv"
        vendname = dirname + "/" + dirname + "-vendors.csv"
        gmlfile = open(gmlname,"w")
        symfile = open(symname,"w")
        csvfile = open(csvname,"r")
        assocfile = open(assocname,"r")
        pubfile = open(pubname,"r")
        vendfile = open(vendname,"r")
        #
        # Read association, publisher, and vendor lists (strip off trailing "\n")
        #
        lines = assocfile.readlines()
        associations = []
        for line in lines:
            associations.append(line.rstrip())
        #
        lines = pubfile.readlines()
        publishers = []
        for line in lines:
            publishers.append(line.rstrip())
        #
        lines = vendfile.readlines()
        vendors = []
        for line in lines:
            vendors.append(line.strip())
        #
        # Close association, publisher, and vendor lists files.
        #
        assocfile.close()
        pubfile.close()
        vendfile.close()  
        #
        # Write graphml header to files
        #
        write_header(gmlfile, "JournalList Ecosystem Graph - All Links")
        write_header(symfile, "JournalList Ecosystem Graph - Symmetric Links Only")
        #
        # Write legend nodes and edges (no need for missing_trust.txt_file in symmetric version)
        #
        write_node(gmlfile,"https://www.association.com/",association)
        write_node(gmlfile,"https://www.publisher.com/",publisher)
        write_node(gmlfile,"https://www.vendor.com/",vendor)
        write_node(gmlfile,"https://missing_trust.txt_file/","#FF0000")
        write_biedge(gmlfile,"https://www.association.com/","https://www.publisher.com/","member","belongto")
        write_uniedge(gmlfile,"https://www.publisher.com/","https://www.vendor.com/","vendor")
        write_uniedge(gmlfile,"https://www.publisher.com/","https://missing_trust.txt_file/","control")
        #
        write_node(symfile,"https://www.association.com/",association)
        write_node(symfile,"https://www.publisher.com/",publisher)
        write_node(symfile,"https://www.vendor.com/",vendor)
        write_node(symfile,"https://missing_trust.txt_file/","#FF0000")
        write_biedge(symfile,"https://www.association.com/","https://www.publisher.com/","member","belongto")
        write_uniedge(symfile,"https://www.publisher.com/","https://www.vendor.com/","vendor")
        write_uniedge(symfile,"https://www.publisher.com/","https://missing_trust.txt_file/","control")
        #
        # Read in the symmetric.csv file and process each line.
        #
        lines = csvfile.readlines()
        #
        for line in lines:
            #
            # Skip the header line
            #
            if ("srcurl" in line):
                continue
            #
            temp = line.split(",",2)
            srcurl = temp[0].strip()
            attr = temp[1].strip()
            refurl = temp[2].strip()
            #
            # Determine edge labels.
            #
            if (attr == "member"):
                forward = "member"
                backward = "belongto"
            elif (attr == "control"):
                forward = "control"
                backward = "controlledby"
            else:
                forward = "vendor"
                backward = "customer"
            #
            # Determine node colors
            #
            if (srcurl in associations):
                srccolor = association
            elif (srcurl in publishers):
                srccolor = publisher
            elif (srcurl in vendors):
                srccolor = vendor
            else:
                srccolor = "#FFFFFF"
            #
            if (refurl in associations):
                refcolor = association
            elif (refurl in publishers):
                refcolor = publisher
            elif (refurl in vendors):
                refcolor = vendor
            else:
                refcolor = "#FFFFFF"
            #
            # Add srcurl and refurl to node list and write the node definition to the gmlfile and symfile if they aren't already in the node list.
            #
            if (srcurl not in nodelist):
                nodelist.append(srcurl)
                write_node(gmlfile,srcurl,srccolor)
                write_node(symfile,srcurl,srccolor)
            if (refurl not in nodelist):
                nodelist.append(refurl)
                write_node(gmlfile,refurl,refcolor)
                write_node(symfile,refurl,refcolor)
            #
            # Write the edge definition to the gmlfile and symfile.
            #
            write_biedge(gmlfile, srcurl, refurl, forward, backward)
            write_biedge(symfile, srcurl, refurl, forward, backward)
        #
        # Write the tail of the symfile and close it.
        #
        write_tail(symfile)
        symfile.close()
        csvfile.close()
    else:
        print (csvname, "doesn't exist")
    #
    # Check if asymmetric.csv file exists
    #
    asymnodelist = []
    csvname = dirname + "/" + dirname + "-asymmetric.csv"
    if(os.path.isfile(csvname)):
        #
        # Read asymmetric.csv file, process content and write to both full and symmetric graphml files.
        #
        asymname = dirname + "/" + dirname + "-asymmetric.graphml"
        csvfile = open(csvname,"r")
        asymfile = open(asymname,"w")
        #
        # Write graphml header to file
        #
        write_header(asymfile, "JournalList Ecosystem Graph - Asymmetric Links Only")
        #
        # Write legend nodes and edges.
        #
        write_node(asymfile,"https://www.association.com/",association)
        write_node(asymfile,"https://www.publisher.com/",publisher)
        write_node(asymfile,"https://www.vendor.com/",vendor)
        write_node(asymfile,"https://missing_trust.txt_file/","#FF0000")
        write_biedge(asymfile,"https://www.association.com/","https://www.publisher.com/","member","belongto")
        write_uniedge(asymfile,"https://www.publisher.com/","https://www.vendor.com/","vendor")
        write_uniedge(asymfile,"https://www.publisher.com/","https://missing_trust.txt_file/","control")
        #
        # Read in the asymmetric.csv file and process each line.
        #
        lines = csvfile.readlines()
        #
        for line in lines:
            #
            # Skip the header line
            #
            if ("srcurl" in line):
                continue
            #
            temp = line.split(",",2)
            srcurl = temp[0]
            attr = temp[1]
            refurl = temp[2].strip()
            #
            # Determine edge labels.
            #
            if (attr == "member"):
                forward = "member"
                backward = "belongto"
            elif (attr == "control"):
                forward = "control"
                backward = "controlledby"
            else:
                forward = "vendor"
                backward = "customer"
            #
            # Determine node colors
            #
            if (srcurl in associations):
                srccolor = association
            elif (srcurl in publishers):
                srccolor = publisher
            elif (srcurl in vendors):
                srccolor = vendor
            else:
                srccolor = "#FFFFFF"
            #
            refcolor = "#FF0000"
            #
            # Add srcurl and refurl to node list and write the node definition to the gmlfile and asymfile if they aren't already in the node list.
            #
            if (srcurl not in nodelist):
                nodelist.append(srcurl)
                write_node(gmlfile,srcurl,srccolor)
            if (refurl not in nodelist):
                nodelist.append(refurl)
                write_node(gmlfile,refurl,refcolor)
            if (srcurl not in asymnodelist):
                asymnodelist.append(srcurl)
                write_node(asymfile,srcurl,srccolor)
            if (refurl not in asymnodelist):
                asymnodelist.append(refurl)
                write_node(asymfile,refurl,refcolor)
            #
            # Write the edge definition to the gmlfile and asymfile.
            #
            write_uniedge(gmlfile, srcurl, refurl, forward)
            write_uniedge(asymfile, srcurl, refurl, forward)
            #
            # Write the tail of the gmfile and asymfile, then close them.
            #
        write_tail(asymfile)
        write_tail(gmlfile)
        gmlfile.close()
        asymfile.close()
        csvfile.close()            
    else:
        print (csvname, "doesn't exist")
else:
    print (dirname, "doesn't exist")