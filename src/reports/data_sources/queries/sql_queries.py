# sample queries
QUERIES = {
    'View1': """
    SELECT
        f.BusinessNameLine1 AS FilerName,
        f.AddressLine1 AS FilerAddress,
        f.City AS FilerCity,
        f.State AS FilerState,
        f.ZIPCode AS FilerZIP,
        g.RecipientName AS GrantRecipientName,
        g.Purpose AS GrantPurpose,
        g.Amount AS GrantAmount
    FROM
        filer f
    JOIN
        return r ON f.EIN = r.EIN
    JOIN
        grantsandcontributions g ON r.ReturnId = g.ReturnId
        limit 10;
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
