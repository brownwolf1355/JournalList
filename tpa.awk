#!awk
# vpa.awk - generate trust.txt files from .csv file containing the following columns:
#
# Name of Paper, Website, Contact, Facebook, Instagram, Twitter, Youtube, LinkedIn, Pinterest, Vendor, Copyright, Control
#
#
# Usage: awk -F "," -f tpa.awk tpa-output.csv
{
    # Skip header row
    #
    if (NR > 1)
    {
        # Remove "http[s]://" from Website, convert "/" to "-", and append "-trust.txt" to form output file name.
        #
        i = index($2, "://")
        temp = substr($2,i + 3)
        gsub("/","-",temp)
        output = temp "trust.txt"
        printf "# %s trust.txt file\n", $1 > output
        printf "#\n" >> output
        printf "# For more information on trust.txt see:\n" >> output
        printf "# 1. https://journallist.net - Home of the trust.txt specification\n" >> output
        printf "# 2. https://datatracker.ietf.org/doc/html/rfc8615 - IETF RFC 8615 - Well-Known Uniform Resource Identifiers (URIs)\n" >> output
        printf "# 3. https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml - IANA's list of registered Well-Known URIs\n" >> output
        if ( length($12) > 1 )
        {
             printf "Website = %s, Control = %s\n", $2, $12
             if ( $2 != $12)
             {
                 printf "#\n" >> output
                 printf "# %s is controlled by the following organization\n", $1 >> output
                 printf "#\n" >> output
                 printf "controlledby=%s\n", $12 >> output
            }
        }
        printf "#\n" >> output
        printf "# %s belongs to the following organizations\n", $1 >> output
        printf "#\n" >> output
        printf "belongto=https://www.texaspress.com/\n" >> output
        printf "belongto=https://journallist.net\n" >> output
        printf "#\n" >> output
        printf "# %s social networks\n", $1 >> output
        printf "#\n" >> output
        if ( $4 != "" ) printf "social=%s\n", $4 >> output
        if ( $5 != "" ) printf "social=%s\n", $5 >> output
        if ( $6 != "" ) printf "social=%s\n", $6 >> output
        if ( $7 != "" ) printf "social=%s\n", $7 >> output
        if ( $8 != "" ) printf "social=%s\n", $8 >> output
        if ( $9 != "" ) printf "social=%s\n", $9 >> output
        if ( $4 == "" && $5 == "" && $6 == "" && $7 == "" && $8 == "" && $9 == "") printf "# social=\n" >> output
        printf "#\n" >> output
        printf "# %s vendors\n", $1 >> output
        printf "#\n" >> output
        if ( $10 != "" )
            printf "vendor=%s\n", $10 >> output
        else
            printf "# vendor=\n" >> output
        printf "#\n" >> output
        printf "# %s contact info\n", $1 >> output
        printf "#\n" >> output
        if ( $3 != "" )
            printf "contact=%s\n", $3 >> output
        else
            printf "# contact=\n" >> output
        if ( $11 != "") printf "#\n# Copyright %s\n", $11 >> output
        close(output)
    }
}
