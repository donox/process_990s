/*
Links Return to PreparerFirm
From XML location in ReturnHeader/PreparerFirmGrp
*/
CREATE TABLE ReturnPreparer (
    ReturnId INTEGER,
    PreparerFirmEIN VARCHAR(9),
    PRIMARY KEY (ReturnId, PreparerFirmEIN),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId),
    FOREIGN KEY (PreparerFirmEIN) REFERENCES PreparerFirm(PreparerFirmEIN)
);