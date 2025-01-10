/*
From XML:
<MinimumInvestmentReturnGrp>
    <AverageMonthlyFMVOfSecAmt>923422</AverageMonthlyFMVOfSecAmt>
    <AverageMonthlyCashBalancesAmt>17718</AverageMonthlyCashBalancesAmt>
    <FMVAllOtherNoncharitableAstAmt>0</FMVAllOtherNoncharitableAstAmt>
    <TotalFMVOfUnusedAssetsAmt>941140</TotalFMVOfUnusedAssetsAmt>
    <AdjustedTotalFMVOfUnusedAstAmt>941140</AdjustedTotalFMVOfUnusedAstAmt>
    <CashDeemedCharitableAmt>14117</CashDeemedCharitableAmt>
    <NetVlNoncharitableAssetsAmt>927023</NetVlNoncharitableAssetsAmt>
    <MinimumInvestmentReturnAmt>46351</MinimumInvestmentReturnAmt>
*/
CREATE TABLE MinimumInvestmentReturn (
    ReturnId INTEGER PRIMARY KEY,
    AverageMonthlyFMVOfSecurities DECIMAL(15,2),
    AverageMonthlyCashBalances DECIMAL(15,2),
    FMVAllOtherNoncharitableAssets DECIMAL(15,2),
    TotalFMVOfUnusedAssets DECIMAL(15,2),
    AdjustedTotalFMVOfUnusedAssets DECIMAL(15,2),
    CashDeemedCharitable DECIMAL(15,2),
    NetValueNoncharitableAssets DECIMAL(15,2),
    MinimumInvestmentReturn DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);