/*
From XML:
<ReturnHeader>
    <ReturnTs>2023-01-13T14:24:16-05:00</ReturnTs>
    <TaxPeriodEndDt>2022-08-31</TaxPeriodEndDt>
    <ReturnTypeCd>990PF</ReturnTypeCd>
    <TaxPeriodBeginDt>2021-09-01</TaxPeriodBeginDt>
    <TaxYr>2021</TaxYr>
And from IRS990PF:
    <Organization501c3ExemptPFInd>X</Organization501c3ExemptPFInd>
    <FMVAssetsEOYAmt>914737</FMVAssetsEOYAmt>
    <MethodOfAccountingCashInd>X</MethodOfAccountingCashInd>
*/
CREATE TABLE Return (
    ReturnId SERIAL PRIMARY KEY,
    EIN VARCHAR(9),
    TaxPeriodEnd DATE,
    TaxPeriodBegin DATE,
    ReturnTs TIMESTAMP,
    ReturnType VARCHAR(10),
    TaxYear INTEGER,
    BuildTs TIMESTAMP,
    Organization501c3ExemptPF BOOLEAN,
    FMVAssetsEOY DECIMAL(15,2),
    MethodOfAccountingCash BOOLEAN,
    FOREIGN KEY (EIN) REFERENCES Filer(EIN)
);