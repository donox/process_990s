/*
From XML:
<AnalysisOfRevenueAndExpenses>
    <InterestOnSavRevAndExpnssAmt>2</InterestOnSavRevAndExpnssAmt>
    <InterestOnSavNetInvstIncmAmt>2</InterestOnSavNetInvstIncmAmt>
    <DividendsRevAndExpnssAmt>31313</DividendsRevAndExpnssAmt>
    <DividendsNetInvstIncmAmt>31313</DividendsNetInvstIncmAmt>
    <NetGainSaleAstRevAndExpnssAmt>-8320</NetGainSaleAstRevAndExpnssAmt>
    <TotalRevAndExpnssAmt>22995</TotalRevAndExpnssAmt>
    <TotalNetInvstIncmAmt>31315</TotalNetInvstIncmAmt>
    <CompOfcrDirTrstRevAndExpnssAmt>4400</CompOfcrDirTrstRevAndExpnssAmt>
    <TotalExpensesRevAndExpnssAmt>47668</TotalExpensesRevAndExpnssAmt>
    <ExcessRevenueOverExpensesAmt>-24673</ExcessRevenueOverExpensesAmt>
*/
CREATE TABLE RevenueAndExpenses (
    ReturnId INTEGER PRIMARY KEY,
    InterestOnSavings DECIMAL(15,2),
    InterestOnSavingsNetInvestment DECIMAL(15,2),
    DividendsRevenue DECIMAL(15,2),
    DividendsNetInvestment DECIMAL(15,2),
    NetGainSaleAssets DECIMAL(15,2),
    TotalRevenue DECIMAL(15,2),
    TotalNetInvestment DECIMAL(15,2),
    CompensationOfficersDirectors DECIMAL(15,2),
    TotalExpenses DECIMAL(15,2),
    ExcessRevenueOverExpenses DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);