# queries used in reporting
QUERIES = {
    # Collect data on an individual filer including contacts and grants made.
    'FilerSummary':
    """
    SELECT f.businessnameline1 as Foundation,
    f,phonenum as Phone,
    f.addressline1 as Address,
    f.city as City,
    f.state as State,
    f.zipcode as Zip,
    r.taxyear as TaxYear,
    d.distributableasadjusted as AvailableFunds
    FROM 
        filer f
    JOIN 
    return r on f.EIN = r.EIN
    JOIN 
    distributableamount d on r.returnid = d.returnid
    where f.EIN = %s
    """,
    # Information about contacts for a specific filer
    'Contacts': """
    SELECT 
        c.personname as Name,
        c.addressline1 as Address,
        c.city as City,
        c.state as State,
        c.zipcode as Zip,
        c.title as Title
    FROM
        keycontacts c
    WHERE
     c.EIN = %s;
    """,

    # Core information about the grants from a specific filer
    'Grants': """
    SELECT
        r.taxyear AS TaxYear,
        g.RecipientName AS GrantRecipientName,
        g.Purpose AS GrantPurpose,
        g.Amount AS GrantAmount
    FROM
        filer f
    JOIN
        return r ON f.EIN = r.EIN
    JOIN
        grantsandcontributions g ON r.ReturnId = g.ReturnId
    WHERE
        f.EIN = %s;

    """,

    # Grants and filers as base for searching relevant grants (returns about 1.4M grants)
    "GrantSearch":
    """
        SELECT
            * 
        FROM
            grantsbyfiler;
    """,
    "View2": """
        SELECT
            f.EIN AS FilerID,
            r.taxyear AS TaxYear,
            f.ZIPCode AS FilerZIP,
            d.DistributableASAdjusted
        FROM
            filer f
        JOIN
            return r ON f.EIN = r.EIN
        JOIN
            distributableamount d ON r.ReturnId = d.ReturnId
            limit 10;
        """
}
