/*
From XML:
<GrantOrContributionPdDurYrGrp>
    <RecipientBusinessName>
        <BusinessNameLine1Txt>POCUMTUCK VALLEY MEMORIAL ASSOC</BusinessNameLine1Txt>
    </RecipientBusinessName>
    <RecipientUSAddress>
        <AddressLine1Txt>10 MEMORIAL STREET</AddressLine1Txt>
        <CityNm>DEERFIELD</CityNm>
        <StateAbbreviationCd>MA</StateAbbreviationCd>
        <ZIPCd>01342</ZIPCd>
    </RecipientUSAddress>
    <RecipientRelationshipTxt>NONE</RecipientRelationshipTxt>
    <GrantOrContributionPurposeTxt>MUSEUM NEEDS</GrantOrContributionPurposeTxt>
    <Amt>40000</Amt>
*/
CREATE TABLE GrantsAndContributions (
    ReturnId INTEGER,
    GrantId SERIAL,
    RecipientName VARCHAR(255),
    AddressLine1 VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(2),
    ZIPCode VARCHAR(10),
    RecipientRelationship VARCHAR(100),
    Purpose TEXT,
    Amount DECIMAL(15,2),
    PRIMARY KEY (ReturnId, GrantId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);