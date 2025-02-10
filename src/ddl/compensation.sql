/*
From XML:
<OfficerDirTrstKeyEmplInfoGrp>
    <OfficerDirTrstKeyEmplGrp>
        <PersonNm>TIMOTHY MCGOURTY</PersonNm>
        <TitleTxt>PRESIDENT</TitleTxt>
        <AverageHrsPerWkDevotedToPosRt>0.00</AverageHrsPerWkDevotedToPosRt>
        <CompensationAmt>0</CompensationAmt>
        <EmployeeBenefitProgramAmt>0</EmployeeBenefitProgramAmt>
        <ExpenseAccountOtherAllwncAmt>0</ExpenseAccountOtherAllwncAmt>
    </OfficerDirTrstKeyEmplGrp>
    <CompOfHghstPdEmplOrNONETxt>NONE</CompOfHghstPdEmplOrNONETxt>
    <CompOfHghstPdCntrctOrNONETxt>NONE</CompOfHghstPdCntrctOrNONETxt>
*/
CREATE TABLE Compensation (
    CompensationId SERIAL PRIMARY KEY,
    ReturnId INTEGER,
    PersonName TEXT,
    Title TEXT,
    AverageHours DECIMAL(10,2),
    Compensation DECIMAL(15,2),
    EmployeeBenefits DECIMAL(15,2),
    ExpenseAccount DECIMAL(15,2),
    HighestPaidEmployeeInfo TEXT,
    HighestPaidContractorInfo TEXT,
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId),
    CONSTRAINT unique_return_person UNIQUE (ReturnId, PersonName)
);