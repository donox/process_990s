/*
From XML:
<GainLossSaleOtherAssetsSch documentId="RetDoc2">
    <GainLossSaleOtherAssetGrp>
        <AssetDesc>1300 SHS ORANGE ADR</AssetDesc>
        <AcquiredDt>2012-03</AcquiredDt>
        <HowAcquiredTxt>PURCHASE</HowAcquiredTxt>
        <SoldDt>2022-04</SoldDt>
        <GrossSalesPriceAmt>14986</GrossSalesPriceAmt>
        <BasisAmt>19162</BasisAmt>
        <TotalNetAmt>-4176</TotalNetAmt>
    </GainLossSaleOtherAssetGrp>
*/
CREATE TABLE AssetSales (
    ReturnId INTEGER,
    AssetId SERIAL,
    AssetDescription VARCHAR(255),
    AcquiredDate DATE,
    HowAcquired VARCHAR(50),
    SoldDate DATE,
    GrossSalesPrice DECIMAL(15,2),
    Basis DECIMAL(15,2),
    TotalNetAmount DECIMAL(15,2),
    PRIMARY KEY (ReturnId, AssetId),
    FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);