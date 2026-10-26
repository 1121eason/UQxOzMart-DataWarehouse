-- Transcribed unchanged in logic from the original report.
WITH SellerSales AS (
    SELECT
        d.[Year],
        s.[name] AS SupplierName,
        SUM(f.QuantitySold) AS TotalQuantitySold
    FROM FactSales f
    INNER JOIN DimSeller s
        ON f.SellerKEY = s.SellerKEY
    INNER JOIN DimDate d
        ON f.DateKEY = d.DateKEY
    WHERE s.State_name = 'New South Wales'
    GROUP BY
        d.[Year],
        s.[name]
),
RankedSellerSales AS (
    SELECT
        [Year],
        SupplierName,
        TotalQuantitySold,
        ROW_NUMBER() OVER (
            PARTITION BY [Year]
            ORDER BY TotalQuantitySold DESC
        ) AS rn
    FROM SellerSales
)
SELECT
    [Year],
    SupplierName,
    TotalQuantitySold
FROM RankedSellerSales
WHERE rn <= 5
ORDER BY [Year], rn;
