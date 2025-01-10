/*
From XML:
<PFQualifyingDistributionsGrp>
    <ExpensesAndContributionsAmt>41229</ExpensesAndContributionsAmt>
    <QualifyingDistributionsAmt>41229</QualifyingDistributionsAmt>
*/
CREATE TABLE QualifyingDistributions (
    ReturnId INTEGER PRIMARY KEY,
    ExpensesAndContributions DECIMAL(15,2),
    QualifyingDistributions DECIMAL(15,2),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);