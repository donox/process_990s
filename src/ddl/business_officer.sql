/*
From XML:
<BusinessOfficerGrp>
    <PersonNm>RUSSELL S ADAMS</PersonNm>
    <PersonTitleTxt>DIRECTOR/MGR</PersonTitleTxt>
    <PhoneNum>4138831047</PhoneNum>
    <SignatureDt>2023-01-04</SignatureDt>
    <DiscussWithPaidPreparerInd>true</DiscussWithPaidPreparerInd>
*/
CREATE TABLE BusinessOfficer (
    ReturnId INTEGER PRIMARY KEY,
    PersonName VARCHAR(255),
    Title VARCHAR(100),
    PhoneNum VARCHAR(20),
    SignatureDate DATE,
    DiscussWithPaidPreparer BOOLEAN,
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);