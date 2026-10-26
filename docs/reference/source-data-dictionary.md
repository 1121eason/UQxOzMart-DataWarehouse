# Source data dictionary

Transcribed from the supplied workbook. Source spellings are preserved. See the [warehouse dictionary](../data-dictionary.md) for implemented target fields.


## Orders_table

| Attribute | Definition |
| --- | --- |
| `order_id` | Unique identifier for each order |
| `customer_id` | Foreign key linking the order to a customer |
| `status` | Current status of the order |
| `purchase_timestamp` | Date and time the order was placed |
| `approved_at` | Date and time the order was approved |
| `delivered_carrier_date` | Date and time the order was handed to the carrier |
| `estimated_delivery_date` | Estimated delivery date/time |
| `delivered_customer_date` | Actual delivery date/time to the customer |

## Order_items_table

| Attribute | Definition |
| --- | --- |
| `order_item_id` | Unique identifier for each order line item |
| `order_id` | Foreign key linking the line item to an order |
| `product_id` | Foreign key linking the line item to a product |
| `seller_id` | Foreign key linking the line item to a seller |
| `item_sequence` | Sequence number of the item within the order |
| `item_quantity` | Quantity of the product ordered |
| `sales_price` | Unit selling price of the product |
| `line_total` | Total amount for the line item |
| `freight_price` | Freight/shipping cost for the line item |
| `shipping_limit_date` | Latest date/time allowed for shipping |

## Product_table

| Attribute | Definition |
| --- | --- |
| `product_id` | Unique identifier for each product |
| `product_name` | Product name |
| `poduct_descriptions` | Product description text |
| `shipping_weight` | Weight of the product for shipping |
| `image` | Product image |
| `product_url` | Product webpage URL |
| `product_subcategorey_id` | Foreign key linking the product to its subcategory |
| `cost_price` | Product cost price |
| `sales_price` | Product selling price |

## Product_subcategory

| Attribute | Definition |
| --- | --- |
| `Product_Category_ID` | Foreign key linking the subcategory to a product category |
| `Product_Subcategorey_ID` | Unique identifier for the product subcategory |
| `Product_Subcategory` | Name of the product subcategory |

## Product_category

| Attribute | Definition |
| --- | --- |
| `Product_Categorey_ID` | Unique identifier for the product category |
| `Product_ Category` | Name of the product category |

## Seller_table

| Attribute | Definition |
| --- | --- |
| `seller_id` | Unique identifier for each seller |
| `location_id` | Foreign key linking the seller to a location |
| `name` | Seller name |
| `email_address` | Seller email address |
| `creation_date` | Date and time the seller account was created |
| `end_date` | Date and time the seller account ended or became inactive |

## Seller_location

| Attribute | Definition |
| --- | --- |
| `address_id` | Unique identifier for the seller location |
| `unit` | Unit, apartment, or suite number |
| `street` | Street name |
| `postcode` | Postcode value |
| `suburb` | Suburb name |
| `state` | State code |
| `type` | Seller location type: business/private |
| `status` | Record update status |
| `region` | Region code |

## Customer_table

| Attribute | Definition |
| --- | --- |
| `customer_id` | Unique identifier for each customer |
| `location_id` | Foreign key linking the customer to a address record |
| `First Name` | Customer first name |
| `Last Name` | Customer last name |
| `Gender` | Customer gender code |
| `Age_key` | Foreign key linking to the age lookup table |
| `EDU_id` | Education code for the customer |
| `created_date` | Date and time the customer record was created |

## Customer_address

| Attribute | Definition |
| --- | --- |
| `address_id` | Unique identifier for the seller location |
| `unit` | Unit, apartment, or suite number |
| `street` | Street name |
| `postcode` | Postcode value |
| `suburb` | Suburb name |
| `state` | State code |
| `type` | Customer address delivery type |
| `status` | Record update status |
| `region` | Region code |

## Address_type

| Attribute | Definition |
| --- | --- |
| `type_id` | Unique identifier for the address/location type |
| `location_type` | Description of the location delivery type |

## Age_table

| Attribute | Definition |
| --- | --- |
| `Age_Id` | Unique key for an age value |
| `Age` | Customer age |

## Customer_Education

| Attribute | Definition |
| --- | --- |
| `EDU_ID` | Unique identifier for an education level |
| `Education_level` | Description of the education level |

## State_code

| Attribute | Definition |
| --- | --- |
| `state_name` | Full state or territory name |
| `state_code` | Abbreviated state or territory code (PK) |
