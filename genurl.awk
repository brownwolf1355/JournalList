BEGIN { print "[" }
{
    if (NR != NL)
        printf "{\"_id\":\"urls/%i\",\"_key\":\"%i\",\"url\":\"%s\",\"class\":\"\",\"controlled\":\"\",\"ctrlcnt\":0,\"nlinks\":0,\"total\":0,\"average\":0},\n", NR, NR, $1 
    else
        printf "{\"_id\":\"urls/%i\",\"_key\":\"%i\",\"url\":\"%s\",\"class\":\"\",\"controlled\":\"\",\"ctrlcnt\":0,\"nlinks\":0,\"total\":0,\"average\":0}\n", NR, NR, $1
}
END { print "]" }
