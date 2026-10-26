-- Original question 2. Product type means category plus subcategory; state is customer's.
WITH ProductSales AS (
    SELECT c.state_name, p.Product_Category, p.Product_Subcategory,
           SUM(CAST(f.QuantitySold AS bigint)) AS TotalQuantitySold
    FROM FactSales f
    JOIN DimCustomer c ON f.CustomerKEY = c.CustomerKEY
    JOIN DimProduct p ON f.ProductKEY = p.ProductKEY
    GROUP BY c.state_name, p.Product_Category, p.Product_Subcategory
), Ranked AS (
    SELECT state_name, Product_Category, Product_Subcategory, TotalQuantitySold,
           ROW_NUMBER() OVER (
               PARTITION BY state_name
               ORDER BY TotalQuantitySold DESC, Product_Category, Product_Subcategory
           ) AS rn
    FROM ProductSales
)
SELECT state_name, Product_Category, Product_Subcategory, TotalQuantitySold
FROM Ranked
WHERE rn <= 5
ORDER BY state_name, rn;
