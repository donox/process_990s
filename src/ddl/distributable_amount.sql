/*
From XML:
<DistributableAmountGrp>
    <MinimumInvestmentReturnAmt>46351</MinimumInvestmentReturnAmt>
    <TaxBasedOnInvestmentIncomeAmt>346</TaxBasedOnInvestmentIncomeAmt>
    <TotalTaxAmt>346</TotalTaxAmt>
    <DistributableBeforeAdjAmt>46005</DistributableBeforeAdjAmt>
    <DistributableBeforeDedAmt>46005</DistributableBeforeDedAmt>
    <DistributableAsAdjustedAmt>46005</DistributableAsAdjustedAmt>
*/
CREATE TABLE DistributableAmount (
    ReturnId INTEGER PRIMARY KEY,
    MinimumInvestmentReturn DECIMAL(15,2),
    TaxBasedOnInvestmentIncome DECIMAL(15,2),
    TotalTax DECIMAL(15,2),
    DistributableBeforeAdj DECIMAL(15,2),
    DistributableBeforeDed DECIMAL(15,2),
    DistributableAsAdjusted DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);