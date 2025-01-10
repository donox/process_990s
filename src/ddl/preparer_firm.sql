/*
From XML:
<PreparerFirmGrp>
    <PreparerFirmEIN>043289146</PreparerFirmEIN>
    <PreparerFirmName>
        <BusinessNameLine1Txt>PIETRAS WERENSKI & CO PC</BusinessNameLine1Txt>
    </PreparerFirmName>
    <PreparerUSAddress>
        <AddressLine1Txt>439 GRANBY RD</AddressLine1Txt>
        <CityNm>SOUTH HADLEY</CityNm>
        <StateAbbreviationCd>MA</StateAbbreviationCd>
        <ZIPCd>010752213</ZIPCd>
    </PreparerUSAddress>
*/
CREATE TABLE PreparerFirm (
    PreparerFirmEIN VARCHAR(9) PRIMARY KEY,
    FirmName VARCHAR(255),
    AddressLine1 VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(2),
    ZIPCode VARCHAR(10)
);