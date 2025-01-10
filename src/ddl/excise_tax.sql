/*
From XML:
<ExciseTaxBasedOnInvstIncmGrp>
    <InvestmentIncomeExciseTaxAmt>346</InvestmentIncomeExciseTaxAmt>
    <SubtotalAmt>346</SubtotalAmt>
    <TaxBasedOnInvestmentIncomeAmt>346</TaxBasedOnInvestmentIncomeAmt>
    <TaxDueAmt>346</TaxDueAmt>
*/
CREATE TABLE ExciseTax (
    ReturnId INTEGER PRIMARY KEY,
    InvestmentIncomeExciseTax DECIMAL(15,2),
    Subtotal DECIMAL(15,2),
    TaxBasedOnInvestmentIncome DECIMAL(15,2),
    TaxDue DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);