-- Transcribed unchanged in logic from the original report.
WITH AgeRevenue AS (
    SELECT
        c.state_name,
        c.Age,
        SUM(f.Revenue) AS TotalRevenue
    FROM FactSales f
    INNER JOIN DimCustomer c
        ON f.CustomerKEY = c.CustomerKEY
    GROUP BY
        c.state_name,
        c.Age
),
RankedAgeRevenue AS (
    SELECT
        state_name,
        Age,
        TotalRevenue,
        ROW_NUMBER() OVER (
            PARTITION BY state_name
            ORDER BY TotalRevenue DESC
        ) AS rn
    FROM AgeRevenue
)
SELECT
    state_name,
    Age AS MostImportantCustomerAge,
    TotalRevenue
FROM RankedAgeRevenue
WHERE rn = 1
ORDER BY state_name;
