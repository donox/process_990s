/*
From XML:
<StatementsRegardingActy4720Grp>
   <SaleOrExchDisqualifiedPrsnInd>false</SaleOrExchDisqualifiedPrsnInd>
   <BrrwOrLendDisqualifiedPrsnInd>false</BrrwOrLendDisqualifiedPrsnInd>
   <FurnGoodsDisqualifiedPrsnInd>false</FurnGoodsDisqualifiedPrsnInd>
   <PayCompDisqualifiedPrsnInd>false</PayCompDisqualifiedPrsnInd>
   <TransferAstDisqualifiedPrsnInd>false</TransferAstDisqualifiedPrsnInd>
   <PaymentToGovernmentOfficialInd>false</PaymentToGovernmentOfficialInd>
   <UndistributedIncomePYInd>false</UndistributedIncomePYInd>
   <BusinessHoldingsInd>false</BusinessHoldingsInd>
   <JeopardyInvestmentsInd>false</JeopardyInvestmentsInd>
   <UncorrectedPYJeopardyInvstInd>false</UncorrectedPYJeopardyInvstInd>
   <InfluenceLegislationInd>false</InfluenceLegislationInd>
   <InfluenceElectionInd>false</InfluenceElectionInd>
   <GrantsToIndividualsInd>false</GrantsToIndividualsInd>
   <GrantsToOrganizationsInd>false</GrantsToOrganizationsInd>
   <NoncharitablePurposeInd>false</NoncharitablePurposeInd>
   <RcvFndsToPayPrsnlBnftCntrctInd>false</RcvFndsToPayPrsnlBnftCntrctInd>
   <PayPremiumsPrsnlBnftCntrctInd>false</PayPremiumsPrsnlBnftCntrctInd>
   <ProhibitedTaxShelterTransInd>false</ProhibitedTaxShelterTransInd>
   <SubjToTaxRmnrtnExPrchtPymtInd>false</SubjToTaxRmnrtnExPrchtPymtInd>
*/
CREATE TABLE StatementsRegardingActivities4720 (
   ReturnId INTEGER PRIMARY KEY,
   SaleOrExchDisqualifiedPerson BOOLEAN,
   BorrowOrLendDisqualifiedPerson BOOLEAN,
   FurnishGoodsDisqualifiedPerson BOOLEAN,
   PayCompDisqualifiedPerson BOOLEAN,
   TransferAssetsDisqualifiedPerson BOOLEAN,
   PaymentToGovernmentOfficial BOOLEAN,
   UndistributedIncomePriorYear BOOLEAN,
   BusinessHoldings BOOLEAN,
   JeopardyInvestments BOOLEAN,
   UncorrectedPriorYearJeopardyInvst BOOLEAN,
   InfluenceLegislation BOOLEAN,
   InfluenceElection BOOLEAN,
   GrantsToIndividuals BOOLEAN,
   GrantsToOrganizations BOOLEAN,
   NoncharitablePurpose BOOLEAN,
   ReceiveFundsPersonalBenefitContract BOOLEAN,
   PayPremiumsPersonalBenefitContract BOOLEAN,
   ProhibitedTaxShelterTrans BOOLEAN,
   SubjectToTaxRemunerationPayment BOOLEAN,
   FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);