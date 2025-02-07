/*
From XML:
<Filer>
    <EIN>202900865</EIN>
    <BusinessName>
        <BusinessNameLine1Txt>ADAMS FOUNDATION</BusinessNameLine1Txt>
        <BusinessNameLine2Txt>C/O RUSSELL ADAMS</BusinessNameLine2Txt>
    </BusinessName>
    <BusinessNameControlTxt>ADAM</BusinessNameControlTxt>
    <PhoneNum>4138831047</PhoneNum>
    <USAddress>
        <AddressLine1Txt>349 PEARL STREET</AddressLine1Txt>
        <CityNm>SOUTH HADLEY</CityNm>
        <StateAbbreviationCd>MA</StateAbbreviationCd>
        <ZIPCd>010751053</ZIPCd>
    </USAddress>
*/
CREATE TABLE Filer (
    EIN VARCHAR(9) NOT NULL PRIMARY KEY,
    BusinessNameLine1 VARCHAR(255),
    BusinessNameLine2 VARCHAR(255),
    BusinessNameControl VARCHAR(50),
    PhoneNum VARCHAR(20),
    AddressLine1 VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(2),
    ZIPCode VARCHAR(10)
);