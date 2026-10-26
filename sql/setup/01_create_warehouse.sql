/* SQL Server. Run in SSMS against the intended instance.
   Reconstructed from v101 SSIS destination metadata, with new constraints/indexes.
   No original warehouse DDL or completed warehouse backup was supplied.
   Creates ozmart_dw if absent. Stops if any target table already exists. */
USE master;
GO
IF DB_ID(N'ozmart_dw') IS NULL
    EXEC(N'CREATE DATABASE ozmart_dw');
GO
USE ozmart_dw;
GO
IF OBJECT_ID(N'dbo.DimCustomer', N'U') IS NOT NULL
 OR OBJECT_ID(N'dbo.DimDate', N'U') IS NOT NULL
 OR OBJECT_ID(N'dbo.DimProduct', N'U') IS NOT NULL
 OR OBJECT_ID(N'dbo.DimSeller', N'U') IS NOT NULL
 OR OBJECT_ID(N'dbo.FactSales', N'U') IS NOT NULL
    THROW 50001, 'Target tables already exist. Use a fresh warehouse or review existing tables.', 1;

SET XACT_ABORT ON;
BEGIN TRANSACTION;

CREATE TABLE dbo.DimCustomer (
    CustomerKEY int IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimCustomer PRIMARY KEY,
    customer_id nvarchar(50) NOT NULL CONSTRAINT UQ_DimCustomer_business UNIQUE,
    Age nvarchar(50) NULL,
    Education_level nvarchar(50) NULL,
    state_name nvarchar(50) NULL
);
CREATE TABLE dbo.DimDate (
    DateKEY int IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimDate PRIMARY KEY,
    [Day] int NOT NULL,
    [Month] int NOT NULL,
    [Year] int NOT NULL,
    FullDate datetime NOT NULL CONSTRAINT UQ_DimDate_FullDate UNIQUE,
    CONSTRAINT CK_DimDate_midnight CHECK (FullDate = CONVERT(date, FullDate)),
    CONSTRAINT CK_DimDate_parts CHECK (
        [Day] = DAY(FullDate) AND [Month] = MONTH(FullDate) AND [Year] = YEAR(FullDate))
);
CREATE TABLE dbo.DimProduct (
    ProductKEY int IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimProduct PRIMARY KEY,
    product_id nvarchar(50) NOT NULL CONSTRAINT UQ_DimProduct_business UNIQUE,
    product_name nvarchar(200) NULL,
    poduct_descriptions nvarchar(3050) NULL,
    product_subcategorey_id nvarchar(50) NULL,
    Product_Category_ID nvarchar(50) NULL,
    Product_Subcategory nvarchar(50) NULL,
    Product_Category nvarchar(50) NULL
);
CREATE TABLE dbo.DimSeller (
    SellerKEY int IDENTITY(1,1) NOT NULL CONSTRAINT PK_DimSeller PRIMARY KEY,
    state nvarchar(50) NULL,
    name nvarchar(50) NULL,
    seller_id nvarchar(50) NOT NULL CONSTRAINT UQ_DimSeller_business UNIQUE,
    state_name nvarchar(50) NULL
);
CREATE TABLE dbo.FactSales (
    order_item_id nvarchar(50) NOT NULL CONSTRAINT PK_FactSales PRIMARY KEY,
    ProductKEY int NOT NULL CONSTRAINT FK_FactSales_Product REFERENCES dbo.DimProduct(ProductKEY),
    SellerKEY int NOT NULL CONSTRAINT FK_FactSales_Seller REFERENCES dbo.DimSeller(SellerKEY),
    CustomerKEY int NOT NULL CONSTRAINT FK_FactSales_Customer REFERENCES dbo.DimCustomer(CustomerKEY),
    Revenue float NOT NULL,
    QuantitySold smallint NOT NULL,
    DateKEY int NOT NULL CONSTRAINT FK_FactSales_Date REFERENCES dbo.DimDate(DateKEY)
);
CREATE INDEX IX_FactSales_Customer ON dbo.FactSales(CustomerKEY) INCLUDE (Revenue, QuantitySold);
CREATE INDEX IX_FactSales_Product ON dbo.FactSales(ProductKEY) INCLUDE (QuantitySold);
CREATE INDEX IX_FactSales_SellerDate ON dbo.FactSales(SellerKEY, DateKEY) INCLUDE (QuantitySold, Revenue);
COMMIT;

/* Source spellings and FLOAT/SMALLINT match the package metadata.
   A production redesign should migrate money to DECIMAL and define return,
   status, unknown-member, incremental load and history policies explicitly. */
