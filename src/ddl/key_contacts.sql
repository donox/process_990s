/*
From XML:
<OfficerDirTrstKeyEmplGrp>
    <PersonNm>JENNIFER ATWATER</PersonNm>
    <USAddress>
        <AddressLine1Txt>48 BROOK STREET</AddressLine1Txt>
        <CityNm>EASTHAMPTON</CityNm>
        <StateAbbreviationCd>MA</StateAbbreviationCd>
        <ZIPCd>01027</ZIPCd>
    </USAddress>
    <TitleTxt>SECRETARY</TitleTxt>
    <AverageHrsPerWkDevotedToPosRt>000.00</AverageHrsPerWkDevotedToPosRt>
    <CompensationAmt>0</CompensationAmt>
    <EmployeeBenefitProgramAmt>0</EmployeeBenefitProgramAmt>
    <ExpenseAccountOtherAllwncAmt>0</ExpenseAccountOtherAllwncAmt>
*/
CREATE TABLE KeyContacts (
    ContactId SERIAL,
    EIN VARCHAR(9),
    PersonName VARCHAR(255),
    AddressLine1 VARCHAR(255),
    City VARCHAR(100),
    State CHAR(2),
    ZipCode VARCHAR(10),
    Title VARCHAR(100),
    AverageHoursPerWeek DECIMAL(6,2),
    Compensation DECIMAL(12,2),
    EmployeeBenefits DECIMAL(12,2),
    ExpenseAccount DECIMAL(12,2),
    PRIMARY KEY (EIN, ContactId),
    FOREIGN KEY (EIN) REFERENCES Filer(EIN),
    UNIQUE (EIN, PersonName)
);