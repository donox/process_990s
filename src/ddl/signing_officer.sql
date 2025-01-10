/*
From XML:
<SigningOfficerGrp>
    <PersonFullName>
        <PersonFirstNm>RUSSELL S</PersonFirstNm>
        <PersonLastNm>ADAMS</PersonLastNm>
    </PersonFullName>
    <SSN>XXX-XX-XXXX</SSN>
*/
CREATE TABLE SigningOfficer (
    ReturnId INTEGER PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    SSN VARCHAR(11),  -- May want to consider encryption for SSN
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);