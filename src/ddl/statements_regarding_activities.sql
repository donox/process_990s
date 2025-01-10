/*
From XML:
<StatementsRegardingActyGrp>
   <LegislativePoliticalActyInd>false</LegislativePoliticalActyInd>
   <MoreThan100SpentInd>false</MoreThan100SpentInd>
   <Form1120POLFiledInd>false</Form1120POLFiledInd>
   <ActivitiesNotPreviouslyRptInd>false</ActivitiesNotPreviouslyRptInd>
   <ChangesToArticlesOrBylawsInd>false</ChangesToArticlesOrBylawsInd>
   <UnrelatedBusIncmOverLimitInd>false</UnrelatedBusIncmOverLimitInd>
   <OrganizationDissolvedEtcInd>false</OrganizationDissolvedEtcInd>
   <Section508eRqrSatisfiedInd>true</Section508eRqrSatisfiedInd>
   <AtLeast5000InAssetsInd>true</AtLeast5000InAssetsInd>
   <OrgReportOrRegisterStateCd>MA</OrgReportOrRegisterStateCd>
   <Form990PFFiledWithAttyGenInd>true</Form990PFFiledWithAttyGenInd>
   <PrivateOperatingFoundationInd>false</PrivateOperatingFoundationInd>
   <NewSubstantialContributorsInd>false</NewSubstantialContributorsInd>
   <OwnControlledEntityInd>false</OwnControlledEntityInd>
   <DonorAdvisedFundInd>false</DonorAdvisedFundInd>
   <ComplyWithPublicInspRqrInd>true</ComplyWithPublicInspRqrInd>
   <WebsiteAddressTxt>N/A</WebsiteAddressTxt>
   <IndividualWithBooksNm>RUSSELL ADAMS</IndividualWithBooksNm>
   <PhoneNum>4138831047</PhoneNum>
   <LocationOfBooksUSAddress>
       <AddressLine1Txt>349 PEARL STREET</AddressLine1Txt>
       <CityNm>SOUTH HADLEY</CityNm>
       <StateAbbreviationCd>MA</StateAbbreviationCd>
       <ZIPCd>010751053</ZIPCd>
   </LocationOfBooksUSAddress>
   <ForeignAccountsQuestionInd>false</ForeignAccountsQuestionInd>
*/
CREATE TABLE StatementsRegardingActivities (
   ReturnId INTEGER PRIMARY KEY,
   LegislativePoliticalActivity BOOLEAN,
   MoreThan100Spent BOOLEAN,
   Form1120POLFiled BOOLEAN,
   ActivitiesNotPreviouslyReported BOOLEAN,
   ChangesToArticlesOrBylaws BOOLEAN,
   UnrelatedBusIncomeOverLimit BOOLEAN,
   OrganizationDissolved BOOLEAN,
   Section508eRequirementSatisfied BOOLEAN,
   AtLeast5000InAssets BOOLEAN,
   OrgReportOrRegisterState VARCHAR(2),
   Form990PFFiledWithAttyGen BOOLEAN,
   PrivateOperatingFoundation BOOLEAN,
   NewSubstantialContributors BOOLEAN,
   OwnControlledEntity BOOLEAN,
   DonorAdvisedFund BOOLEAN,
   ComplyWithPublicInspection BOOLEAN,
   WebsiteAddress VARCHAR(255),
   IndividualWithBooks VARCHAR(255),
   BooksPhone VARCHAR(20),
   BooksAddressLine1 VARCHAR(255),
   BooksCity VARCHAR(100),
   BooksState VARCHAR(2),
   BooksZIPCode VARCHAR(10),
   ForeignAccounts BOOLEAN,
   FOREIGN KEY (ReturnId) REFERENCES Return(ReturnId)
);