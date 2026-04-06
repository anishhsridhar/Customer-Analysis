create database market;
use market

-- 1) Number of customers from each education level:
SELECT Education,
       COUNT(*) AS Total,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM market_data), 2) AS Percentage
FROM market_data
GROUP BY Education
ORDER BY Total_Customers DESC;

-- 2) Average Age of customers:
SELECT 
    ROUND(AVG(Age), 0) AS Average_Age,
    MIN(Age) AS Youngest,
    MAX(Age) AS Oldest
FROM market_data;


-- 3) Overall response rate:
SELECT 
    COUNT(*) AS Total_Customers,
    SUM(Response) AS Total_Responders,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spend,
    ROUND(SUM(Total_Amt), 2) AS Revenue
FROM market_data;


-- 4) Average amount spent on each product:
SELECT 
    ROUND(AVG(MntWines), 2) AS Wine,
    ROUND(AVG(MntFruits), 2) AS Fruits,
    ROUND(AVG(MntMeatProducts),2) AS Meat,
    ROUND(AVG(MntFishProducts),2) AS Fish,
    ROUND(AVG(MntSweetProducts),2) AS Sweets,
    ROUND(AVG(MntGoldProds), 2) AS Gold
FROM market_data;


-- 5) Amount spent by each age group:
SELECT Age_Group,
       COUNT(*) AS Total,
       ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
       ROUND(AVG(Income), 2) AS Avg_Income
FROM market_data
GROUP BY Age_Group
ORDER BY Avg_Spent DESC;

-- 6) Acceptence rate per campain:
SELECT 
    ROUND(AVG(AcceptedCmp1) * 100, 2) AS Campaign1,
    ROUND(AVG(AcceptedCmp2) * 100, 2) AS Campaign2,
    ROUND(AVG(AcceptedCmp3) * 100, 2) AS Campaign3,
    ROUND(AVG(AcceptedCmp4) * 100, 2) AS Campaign4,
    ROUND(AVG(AcceptedCmp5) * 100, 2) AS Campaign5,
    ROUND(AVG(Response) * 100, 2) AS Response
FROM market_data;

-- 7) Revenue per product:
SELECT 
    ROUND(SUM(MntWines), 2) AS Wine,
    ROUND(SUM(MntFruits), 2) AS Fruits,
    ROUND(SUM(MntMeatProducts), 2) AS Meat,
    ROUND(SUM(MntFishProducts),2) AS Fish,
    ROUND(SUM(MntSweetProducts), 2) AS Sweets,
    ROUND(SUM(MntGoldProds),2) AS Gold,
    ROUND(SUM(Total_Amt),2) AS Total
FROM market_data;


-- 8) Most used channel of purchasing:
SELECT 
    SUM(NumWebPurchases)  AS Web,
    SUM(NumStorePurchases)  AS Store,
    SUM(NumCatalogPurchases) AS Catalog,
    SUM(NumDealsPurchases) AS Deals
FROM market_data;

-- 9) Channels used by different age groups:
SELECT Age_Group,
       ROUND(AVG(NumWebPurchases),2) AS Web,
       ROUND(AVG(NumStorePurchases),2) AS Store,
       ROUND(AVG(NumCatalogPurchases), 2) AS Catalog,
       ROUND(AVG(Total_Purchases), 2) AS Total
FROM market_data
GROUP BY Age_Group
ORDER BY Total DESC;

-- 10) Top 10 most spending customer:
SELECT ID, Age, Age_Group, Education,Income, Income_Group, 
		Total_Amt, Campaigns_Accepted, Response
FROM market_data
ORDER BY Total_Amt DESC
LIMIT 10;

-- 11) Do complainers spend less?
SELECT 
    Complain,
    COUNT(*) AS Total,
    ROUND(AVG(Total_Amt),2) AS Avg_Spent,
    ROUND(AVG(Income),2) AS Avg_Income,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate
FROM market_data
GROUP BY Complain;

-- 12) How many campains customers accepted:
SELECT 
    CASE 
        WHEN Campaigns_Accepted = 0 THEN 'Not accepted'
        WHEN Campaigns_Accepted = 1 THEN 'Once'
        WHEN Campaigns_Accepted = 2 THEN 'Twice'
        ELSE 'Always'
    END AS Campaign_acceptance,
    COUNT(*) AS Total,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
    ROUND(AVG(Income),2) AS Avg_Income
FROM market_data
GROUP BY Campaign_acceptance
ORDER BY Avg_Spent DESC;

-- 13) Complaint rate:
SELECT 
    SUM(Complain) AS Total_Complaints,
    COUNT(*) AS Total_Customers,
    ROUND(SUM(Complain) * 100.0 / COUNT(*), 2) AS Complaint_Rate
FROM market_data;

-- 14) Customers by country:
SELECT Country,
       COUNT(*) AS Total,
       ROUND(AVG(Income), 2) AS Avg_Income
FROM market_data
GROUP BY Country
ORDER BY Total DESC;

-- 15) Education vs Income:
SELECT Education,
       Income_Group,
       COUNT(*) AS Total_Customers,
       ROUND(AVG(Total_Amt),      2) AS Avg_Spent,
       ROUND(AVG(Response) * 100, 2) AS Response_Rate
FROM market_data
GROUP BY Education, Income_Group
ORDER BY Avg_Spent DESC;
