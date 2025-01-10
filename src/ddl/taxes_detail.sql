/*
From XML:
<TaxesSchedule documentId="RetDoc6">
    <TaxesDetail>
        <CategoryTxt>FOREIGN TAX ON DIVIDENDS</CategoryTxt>
        <Amt>179</Amt>
        <NetInvestmentIncomeAmt>179</NetInvestmentIncomeAmt>
    </TaxesDetail>
*/
CREATE TABLE TaxesDetail (
    ReturnId INTEGER,
    TaxId SERIAL,
    Category VARCHAR(255),
    Amount DECIMAL(15,2),
    NetInvestmentIncomeAmount DECIMAL(15,2),
    PRIMARY KEY (ReturnId, TaxId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);