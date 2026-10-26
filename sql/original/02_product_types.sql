-- Transcribed unchanged in logic from the original report.
WITH ProductSales AS (
    SELECT
        c.state_name,
        p.Product_Category,
        p.Product_Subcategory,
        SUM(f.QuantitySold) AS TotalQuantitySold
    FROM FactSales f
    INNER JOIN DimCustomer c
        ON f.CustomerKEY = c.CustomerKEY
    INNER JOIN DimProduct p
        ON f.ProductKey = p.ProductKey
    GROUP BY
        c.state_name,
        p.Product_Category,
        p.Product_Subcategory
),
RankedProductSales AS (
    SELECT
        state_name,
        Product_Category,
        Product_Subcategory,
        TotalQuantitySold,
        ROW_NUMBER() OVER (
            PARTITION BY state_name
            ORDER BY TotalQuantitySold DESC
        ) AS rn
    FROM ProductSales
)
SELECT
    state_name,
    Product_Category,
    Product_Subcategory,
    TotalQuantitySold
FROM RankedProductSales
WHERE rn <= 5
ORDER BY state_name, rn;
