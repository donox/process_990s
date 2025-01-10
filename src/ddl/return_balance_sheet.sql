/*
From XML:
<Form990PFBalanceSheetsGrp>
    <SavAndTempCashInvstBOYAmt>3986</SavAndTempCashInvstBOYAmt>
    <SavAndTempCashInvstEOYAmt>20795</SavAndTempCashInvstEOYAmt>
    <SavAndTempCashInvstEOYFMVAmt>20795</SavAndTempCashInvstEOYFMVAmt>
    <TotalAssetsBOYAmt>483465</TotalAssetsBOYAmt>
    <TotalAssetsEOYAmt>458471</TotalAssetsEOYAmt>
    <TotalAssetsEOYFMVAmt>914737</TotalAssetsEOYFMVAmt>
    <TotalLiabilitiesEOYAmt>0</TotalLiabilitiesEOYAmt>
*/
CREATE TABLE ReturnBalanceSheet (
    ReturnId INTEGER PRIMARY KEY,
    SavingsCashInvestmentsBOY DECIMAL(15,2),
    SavingsCashInvestmentsEOY DECIMAL(15,2),
    SavingsCashInvestmentsEOYFMV DECIMAL(15,2),
    TotalAssetsBOY DECIMAL(15,2),
    TotalAssetsEOY DECIMAL(15,2),
    TotalAssetsEOYFMV DECIMAL(15,2),
    TotalLiabilitiesEOY DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);