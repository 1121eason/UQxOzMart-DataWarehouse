-- SQL Server. Review every result set in the current warehouse after loading.
-- Expected: one row per dimension business key/date, no missing fact keys.
SELECT 'DimCustomer' AS TableName, COUNT_BIG(*) AS RowCount FROM DimCustomer
UNION ALL SELECT 'DimDate', COUNT_BIG(*) FROM DimDate
UNION ALL SELECT 'DimProduct', COUNT_BIG(*) FROM DimProduct
UNION ALL SELECT 'DimSeller', COUNT_BIG(*) FROM DimSeller
UNION ALL SELECT 'FactSales', COUNT_BIG(*) FROM FactSales;

SELECT customer_id, COUNT(*) AS DuplicateCount FROM DimCustomer GROUP BY customer_id HAVING COUNT(*) > 1;
SELECT product_id, COUNT(*) AS DuplicateCount FROM DimProduct GROUP BY product_id HAVING COUNT(*) > 1;
SELECT seller_id, COUNT(*) AS DuplicateCount FROM DimSeller GROUP BY seller_id HAVING COUNT(*) > 1;
SELECT FullDate, COUNT(*) AS DuplicateCount FROM DimDate GROUP BY FullDate HAVING COUNT(*) > 1;
SELECT order_item_id, COUNT(*) AS DuplicateCount FROM FactSales GROUP BY order_item_id HAVING COUNT(*) > 1;

SELECT COUNT_BIG(*) AS OrphanOrNullKeyCount
FROM FactSales f
LEFT JOIN DimCustomer c ON f.CustomerKEY = c.CustomerKEY
LEFT JOIN DimProduct p ON f.ProductKEY = p.ProductKEY
LEFT JOIN DimSeller s ON f.SellerKEY = s.SellerKEY
LEFT JOIN DimDate d ON f.DateKEY = d.DateKEY
WHERE c.CustomerKEY IS NULL OR p.ProductKEY IS NULL OR s.SellerKEY IS NULL OR d.DateKEY IS NULL;

SELECT * FROM DimDate
WHERE FullDate <> CONVERT(date, FullDate)
   OR [Day] <> DAY(FullDate) OR [Month] <> MONTH(FullDate) OR [Year] <> YEAR(FullDate);

-- Investigate non-numeric/missing ages before using numeric tie-breaks in question 1.
SELECT * FROM DimCustomer WHERE TRY_CONVERT(int, Age) IS NULL;
-- Profiling results; these require business review, not an automatic rejection policy.
SELECT COUNT_BIG(*) AS NonPositiveQuantityRows FROM FactSales WHERE QuantitySold <= 0;
SELECT COUNT_BIG(*) AS NegativeRevenueRows FROM FactSales WHERE Revenue < 0;
SELECT state, state_name, COUNT_BIG(*) AS SellerCount
FROM DimSeller GROUP BY state, state_name ORDER BY state, state_name;
