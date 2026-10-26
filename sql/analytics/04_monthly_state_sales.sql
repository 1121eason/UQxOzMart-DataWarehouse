-- Portfolio extension. OrderLines counts fact rows, not distinct orders or customers.
SELECT d.[Year], d.[Month], c.state_name,
       COUNT(*) AS OrderLines,
       SUM(CAST(f.QuantitySold AS bigint)) AS UnitsSold,
       SUM(f.Revenue) AS Revenue
FROM FactSales f
JOIN DimDate d ON f.DateKEY = d.DateKEY
JOIN DimCustomer c ON f.CustomerKEY = c.CustomerKEY
GROUP BY d.[Year], d.[Month], c.state_name
ORDER BY d.[Year], d.[Month], c.state_name;
