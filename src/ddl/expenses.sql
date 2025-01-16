/*
From XML:
<AnalysisOfRevenueAndExpenses>
    <CompOfcrDirTrstRevAndExpnssAmt>0</CompOfcrDirTrstRevAndExpnssAmt>
    <TotOprExpensesRevAndExpnssAmt>824</TotOprExpensesRevAndExpnssAmt>
    <ContriPaidRevAndExpnssAmt>2615</ContriPaidRevAndExpnssAmt>
    <TotalExpensesRevAndExpnssAmt>3439</TotalExpensesRevAndExpnssAmt>
    <AccountingFeesRevAndExpnssAmt>824</AccountingFeesRevAndExpnssAmt>
    <OtherExpensesRevAndExpnssAmt>1767</OtherExpensesRevAndExpnssAmt>
*/
CREATE TABLE Expenses (
    ReturnId INTEGER PRIMARY KEY,
    CompensationAmount DECIMAL(15,2),
    OperatingExpenses DECIMAL(15,2),
    ContributionsPaid DECIMAL(15,2),
    TotalExpenses DECIMAL(15,2),
    AccountingFees DECIMAL(15,2),
    OtherExpenses DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);
