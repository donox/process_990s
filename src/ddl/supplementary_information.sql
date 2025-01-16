/*
From XML:
<SupplementaryInformationGrp>
    <ApplicationSubmissionInfoGrp>
        <FormAndInfoAndMaterialsTxt>APPLICATION SHOULD BE SUBMITTED...</FormAndInfoAndMaterialsTxt>
        <SubmissionDeadlinesTxt>NONE</SubmissionDeadlinesTxt>
        <RestrictionsOnAwardsTxt>AWARDS ARE LIMITED TO...</RestrictionsOnAwardsTxt>
        <RecipientEmailAddressTxt>example@email.com</RecipientEmailAddressTxt>
    </ApplicationSubmissionInfoGrp>
    <TotalGrantOrContriPdDurYrAmt>2615</TotalGrantOrContriPdDurYrAmt>
    <TotalGrantOrContriApprvFutAmt>0</TotalGrantOrContriApprvFutAmt>
    <OnlyContriToPreselectedInd>X</OnlyContriToPreselectedInd>
*/
CREATE TABLE SupplementaryInformation (
    ReturnId INTEGER PRIMARY KEY,
    ApplicationFormInfo TEXT,
    ApplicationDeadlines TEXT,
    ApplicationRestrictions TEXT,
    ApplicationEmail TEXT,
    TotalGrantsPaidDuringYear DECIMAL(15,2),
    TotalGrantsApprovedFuture DECIMAL(15,2),
    OnlyPreselectedContributions BOOLEAN,
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);