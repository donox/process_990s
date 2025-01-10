/*
From XML:
<UndistributedIncomeGrp>
    <DistributableAsAdjustedAmt>46005</DistributableAsAdjustedAmt>
    <ExcessDistributionCyovYr5Amt>561</ExcessDistributionCyovYr5Amt>
    <ExcessDistributionCyovYr3Amt>4091</ExcessDistributionCyovYr3Amt>
    <ExcessDistributionCyovYr2Amt>1231</ExcessDistributionCyovYr2Amt>
    <TotalExcessDistributionCyovAmt>5883</TotalExcessDistributionCyovAmt>
    <QualifyingDistributionsAmt>41229</QualifyingDistributionsAmt>
    <AppliedToCurrentYearAmt>41229</AppliedToCurrentYearAmt>
    <ExcessDistriCyovAppCYCorpusAmt>4776</ExcessDistriCyovAppCYCorpusAmt>
    <ExcessDistributionCyovAppCYAmt>4776</ExcessDistributionCyovAppCYAmt>
    <TotalCorpusAmt>1107</TotalCorpusAmt>
    <UndistributedIncomeCYAmt>0</UndistributedIncomeCYAmt>
    <ExcessDistriCyovToNextYrAmt>1107</ExcessDistriCyovToNextYrAmt>
    <ExcessFromYear2Amt>1107</ExcessFromYear2Amt>
*/
CREATE TABLE UndistributedIncome (
    ReturnId INTEGER PRIMARY KEY,
    DistributableAsAdjusted DECIMAL(15,2),
    ExcessDistributionYear5 DECIMAL(15,2),
    ExcessDistributionYear3 DECIMAL(15,2),
    ExcessDistributionYear2 DECIMAL(15,2),
    TotalExcessDistribution DECIMAL(15,2),
    QualifyingDistributions DECIMAL(15,2),
    AppliedToCurrentYear DECIMAL(15,2),
    ExcessDistributionAppliedToCorpus DECIMAL(15,2),
    ExcessDistributionAppliedToCY DECIMAL(15,2),
    TotalCorpus DECIMAL(15,2),
    UndistributedIncomeCY DECIMAL(15,2),
    ExcessDistributionToNextYear DECIMAL(15,2),
    ExcessFromYear2 DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);