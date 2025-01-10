/*
From XML:
<PreparerPersonGrp>
    <PreparerPersonNm>JOHN E PIETRAS</PreparerPersonNm>
    <PTIN>P00488600</PTIN>
    <PhoneNum>4135335230</PhoneNum>
    <PreparationDt>2023-01-13</PreparationDt>
*/
CREATE TABLE PreparerPerson (
    ReturnId INTEGER PRIMARY KEY,
    PreparerName VARCHAR(255),
    PTIN VARCHAR(9),
    PhoneNum VARCHAR(20),
    PreparationDate DATE,
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);