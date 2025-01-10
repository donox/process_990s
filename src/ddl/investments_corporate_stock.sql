/*
From XML:
<InvestmentsCorporateStockGrp>
    <StockNm>500SHS CATERPILLAR INC</StockNm>
    <EOYBookValueAmt>30256</EOYBookValueAmt>
    <EOYFMVAmt>92355</EOYFMVAmt>
</InvestmentsCorporateStockGrp>
*/
CREATE TABLE InvestmentsCorporateStock (
    ReturnId INTEGER,
    StockId SERIAL,
    StockName VARCHAR(255),
    EOYBookValue DECIMAL(15,2),
    EOYFMV DECIMAL(15,2),
    PRIMARY KEY (ReturnId, StockId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);