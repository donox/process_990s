DROP VIEW IF EXISTS grantsbyfiler;
CREATE VIEW grantsbyfiler AS
SELECT r.ein, g.recipientname as recipient, g.purpose, g.amount
FROM return r
JOIN grantsandcontributions g ON r.returnid = g.returnid;