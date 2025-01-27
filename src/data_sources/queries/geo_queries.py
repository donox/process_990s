# queries used in geo calc
GEO_QUERIES = {
    # Collect data on an individual filer including contacts and grants made.
    'GrantLocations':
    """
    SELECT
    f.ein, 
    f.businessnameline1 as Foundation,
    f.zipcode as Zip,
    g.zipcode as GrantZip,
    g.amount as Amount
    FROM 
        filer f
    JOIN 
    return r on f.EIN = r.EIN
    JOIN 
    grantsandcontributions g on g.returnid = r.returnid
    """,
    'PrincipalsLocations':
        """
        SELECT
        f.ein, 
        f.businessnameline1 as Foundation,
        f.zipcode as Zip,
        g.zipcode as KeyZip,
        g.title as KeyTitle
        FROM 
            filer f
        JOIN 
        keycontacts g on g.EIN = f.EIN
        """,
}