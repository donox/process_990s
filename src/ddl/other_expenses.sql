/*
From XML:
<OtherExpensesSchedule documentId="RetDoc5">
    <OtherExpensesScheduleGrp>
        <Desc>BROKERAGE ACCT FEES</Desc>
        <RevenueAndExpensesPerBooksAmt>200</RevenueAndExpensesPerBooksAmt>
        <NetInvestmentIncomeAmt>200</NetInvestmentIncomeAmt>
    </OtherExpensesScheduleGrp>
*/
CREATE TABLE OtherExpenses (
    ReturnId INTEGER,
    ExpenseId SERIAL,
    Description VARCHAR(255),
    RevenueAndExpensesPerBooks DECIMAL(15,2),
    NetInvestmentIncome DECIMAL(15,2),
    PRIMARY KEY (ReturnId, ExpenseId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);