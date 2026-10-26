-- Original question 1. One winner per customer state; lower age breaks revenue ties.
WITH AgeRevenue AS (
    SELECT c.state_name, c.Age, SUM(f.Revenue) AS TotalRevenue
    FROM FactSales f
    JOIN DimCustomer c ON f.CustomerKEY = c.CustomerKEY
    GROUP BY c.state_name, c.Age
), Ranked AS (
    SELECT state_name, Age, TotalRevenue,
           ROW_NUMBER() OVER (
               PARTITION BY state_name
               ORDER BY TotalRevenue DESC, CAST(Age AS int), Age
           ) AS rn
    FROM AgeRevenue
)
SELECT state_name, Age AS MostImportantCustomerAge, TotalRevenue
FROM Ranked
WHERE rn = 1
ORDER BY state_name;
