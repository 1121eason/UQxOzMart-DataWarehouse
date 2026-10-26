-- SQL Server. Run in ozmart_dw with read access to restored ozmart_db.
-- Original SSIS has no order-status filter; compare the full source population.
SELECT 'Source' AS Population, COUNT_BIG(*) AS OrderLines,
       SUM(CAST(item_quantity AS bigint)) AS Units,
       SUM(CAST(line_total AS decimal(38,4))) AS Revenue
FROM ozmart_db.dbo.order_items_table
UNION ALL
SELECT 'Warehouse', COUNT_BIG(*), SUM(CAST(QuantitySold AS bigint)),
       SUM(CAST(Revenue AS decimal(38,4)))
FROM dbo.FactSales;

-- Expected: zero missing/extra source line IDs after a complete successful full load.
SELECT src.order_item_id AS MissingWarehouseLine
FROM ozmart_db.dbo.order_items_table src
LEFT JOIN dbo.FactSales f ON src.order_item_id = f.order_item_id
WHERE f.order_item_id IS NULL;

SELECT f.order_item_id AS ExtraWarehouseLine
FROM dbo.FactSales f
LEFT JOIN ozmart_db.dbo.order_items_table src ON src.order_item_id = f.order_item_id
WHERE src.order_item_id IS NULL;

-- FLOAT compatibility requires a tolerance; quantity and business-key matches are exact.
SELECT f.order_item_id
FROM dbo.FactSales f
JOIN ozmart_db.dbo.order_items_table src ON f.order_item_id = src.order_item_id
JOIN ozmart_db.dbo.orders_table o ON src.order_id = o.order_id
JOIN dbo.DimCustomer c ON f.CustomerKEY = c.CustomerKEY
JOIN dbo.DimProduct p ON f.ProductKEY = p.ProductKEY
JOIN dbo.DimSeller s ON f.SellerKEY = s.SellerKEY
JOIN dbo.DimDate d ON f.DateKEY = d.DateKEY
WHERE f.QuantitySold <> src.item_quantity
   OR ABS(f.Revenue - CAST(src.line_total AS float)) > 0.0001
   OR c.customer_id <> o.customer_id
   OR p.product_id <> src.product_id
   OR s.seller_id <> src.seller_id
   OR CONVERT(date, d.FullDate) <> CONVERT(date, o.purchase_timestamp);
