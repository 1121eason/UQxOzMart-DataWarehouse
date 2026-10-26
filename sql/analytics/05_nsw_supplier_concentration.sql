-- Portfolio extension. Shares use only units sold by NSW-based sellers in that year.
WITH SellerSales AS (
    SELECT d.[Year], s.seller_id, s.name AS SupplierName,
           SUM(CAST(f.QuantitySold AS bigint)) AS UnitsSold
    FROM FactSales f
    JOIN DimSeller s ON f.SellerKEY = s.SellerKEY
    JOIN DimDate d ON f.DateKEY = d.DateKEY
    WHERE s.state_name = 'New South Wales'
    GROUP BY d.[Year], s.seller_id, s.name
)
SELECT [Year], seller_id, SupplierName, UnitsSold,
       100.0 * UnitsSold / NULLIF(SUM(UnitsSold) OVER (PARTITION BY [Year]), 0) AS UnitSharePct,
       100.0 * SUM(UnitsSold) OVER (
           PARTITION BY [Year] ORDER BY UnitsSold DESC, seller_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) / NULLIF(SUM(UnitsSold) OVER (PARTITION BY [Year]), 0) AS CumulativeUnitSharePct
FROM SellerSales
ORDER BY [Year], UnitsSold DESC, seller_id;
