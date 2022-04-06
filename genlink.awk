BEGIN { print "[" }
{
    NT = NL1 + NL2
    LN = NR - NL1
    if ( FILENAME == "temp1" )
        url[$1] = NR
    else
        if (NR != NT)
            printf "{\"_id\":\"links/%i\",\"_key\":\"%i\",\"from\":\"%s\",\"_from\":\"urls/%s\",\"attr\":\"%s\",\"to\":\"%s\",\"_to\":\"urls/%s\",\"symmetric\":\"\",\"weight\":1},\n", LN, LN, $1, url[$1], $2, $3, url[$3]
        else
            printf "{\"_id\":\"links/%i\",\"_key\":\"%i\",\"from\":\"%s\",\"_from\":\"urls/%s\",\"attr\":\"%s\",\"to\":\"%s\",\"_to\":\"urls/%s\",\"symmetric\":\"\",\"weight\":1}\n", LN, LN, $1, url[$1], $2, $3, url[$3]
}
END { print "]" }
