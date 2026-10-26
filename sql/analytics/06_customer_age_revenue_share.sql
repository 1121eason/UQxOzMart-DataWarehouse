-- Portfolio extension. Revenue share within customer state; no customer-count denominator.
WITH Segments AS (
    SELECT c.state_name, c.Age, COUNT(*) AS OrderLines,
           SUM(CAST(f.QuantitySold AS bigint)) AS UnitsSold,
           SUM(f.Revenue) AS Revenue
    FROM FactSales f
    JOIN DimCustomer c ON f.CustomerKEY = c.CustomerKEY
    GROUP BY c.state_name, c.Age
)
SELECT state_name, Age, OrderLines, UnitsSold, Revenue,
       100.0 * Revenue / NULLIF(SUM(Revenue) OVER (PARTITION BY state_name), 0) AS RevenueSharePct
FROM Segments
ORDER BY state_name, Revenue DESC, CAST(Age AS int), Age;
