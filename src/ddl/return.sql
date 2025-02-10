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
    EIN VARCHAR(9) NOT NULL,
    ReturnFile VARCHAR(30),
    TaxPeriodEnd DATE,
    TaxPeriodBegin DATE,
    ReturnType VARCHAR(10),
    TaxYear INTEGER,
    Organization501c3ExemptPF BOOLEAN,
    FMVAssetsEOY DECIMAL(15,2),
    MethodOfAccountingCash BOOLEAN,
    FileName VARCHAR(200),
    FOREIGN KEY (EIN) REFERENCES Filer(EIN),
    UNIQUE (EIN, TaxYear)
);