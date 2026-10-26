-- Original question 3. Seller state, not customer state. IDs keep namesakes separate.
WITH SellerSales AS (
    SELECT d.[Year], s.seller_id, s.name AS SupplierName,
           SUM(CAST(f.QuantitySold AS bigint)) AS TotalQuantitySold
    FROM FactSales f
    JOIN DimSeller s ON f.SellerKEY = s.SellerKEY
    JOIN DimDate d ON f.DateKEY = d.DateKEY
    WHERE s.state_name = 'New South Wales'
    GROUP BY d.[Year], s.seller_id, s.name
), Ranked AS (
    SELECT [Year], seller_id, SupplierName, TotalQuantitySold,
           ROW_NUMBER() OVER (
               PARTITION BY [Year]
               ORDER BY TotalQuantitySold DESC, seller_id
           ) AS rn
    FROM SellerSales
)
SELECT [Year], seller_id, SupplierName, TotalQuantitySold
FROM Ranked
WHERE rn <= 5
ORDER BY [Year], rn;
