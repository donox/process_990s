/*
From XML:
<AccountingFeesSchedule documentId="RetDoc1">
    <AccountingFeesDetail>
        <CategoryTxt>PIETRAS WERENSKI & CO PC</CategoryTxt>
        <Amt>2800</Amt>
        <NetInvestmentIncomeAmt>2800</NetInvestmentIncomeAmt>
    </AccountingFeesDetail>
*/
CREATE TABLE AccountingFees (
    ReturnId INTEGER,
    FeeId SERIAL,
    Category VARCHAR(255),
    Amount DECIMAL(15,2),
    NetInvestmentIncomeAmount DECIMAL(15,2),
    PRIMARY KEY (ReturnId, FeeId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);