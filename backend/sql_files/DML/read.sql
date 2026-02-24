USE `sql3817488`;



-- List of Views to Fufill any needed READ Operations






-- View: Customers browse data with computed active order count.
CREATE OR REPLACE VIEW v_browse_customers_page AS
SELECT Customers.customerID AS "Customer ID",
       Customers.firstName AS "First Name",
       Customers.lastName AS "Last Name",
       Customers.email AS "Email",
       Customers.phoneNumber AS "Phone Number",
       COUNT(Orders.orderID) AS "Active Orders"
FROM Customers
LEFT JOIN Orders
       ON Orders.customerID = Customers.customerID
GROUP BY Customers.customerID,
         Customers.firstName,
         Customers.lastName,
         Customers.email,
         Customers.phoneNumber
ORDER BY Customers.customerID;

-- View: Orders browse data joined to customer and employee names.
CREATE OR REPLACE VIEW v_browse_orders_page AS
SELECT Orders.orderID AS "Order ID",
       Orders.orderDate AS "Order Date",
       Orders.orderTotal AS "Order Total",
       Customers.customerID AS "Customer ID",
       Customers.firstName AS "First Name",
       Customers.lastName AS "Last Name",
       Employees.employeeID AS "Employee ID",
       Employees.firstName AS "Employee First Name",
       Employees.lastName AS "Employee Last Name"
FROM Orders
LEFT JOIN Customers
       ON Orders.customerID = Customers.customerID
LEFT JOIN Employees
       ON Orders.employeeID = Employees.employeeID
ORDER BY Orders.orderID;

-- View: Order details browse data with product names and computed line totals.
CREATE OR REPLACE VIEW v_browse_order_details_page AS
SELECT OrderDetails.orderDetailsID AS "Order Details ID",
       OrderDetails.orderID AS "Order ID",
       Products.productID AS "Product ID",
       Products.productName AS "Product Name",
       OrderDetails.quantity AS "Quantity",
       OrderDetails.unitPrice AS "Unit Price",
       (OrderDetails.quantity * OrderDetails.unitPrice) AS "Line Total"
FROM OrderDetails
LEFT JOIN Products
       ON OrderDetails.productID = Products.productID
ORDER BY OrderDetails.orderDetailsID;

-- View: Products browse data with type details and units sold.
CREATE OR REPLACE VIEW v_browse_products_page AS
SELECT Products.productID AS "Product ID",
       Products.productName AS "Product Name",
       ProductTypes.productTypeCode AS "Product Type Code",
       ProductTypes.productTypeName AS "Product Type Name",
       Products.price AS "Price",
       Products.stock AS "Stock",
       COALESCE(SUM(OrderDetails.quantity), 0) AS "Units Sold"
FROM Products
LEFT JOIN ProductTypes
       ON Products.productTypeCode = ProductTypes.productTypeCode
LEFT JOIN OrderDetails
       ON OrderDetails.productID = Products.productID
GROUP BY Products.productID,
         Products.productName,
         ProductTypes.productTypeCode,
         ProductTypes.productTypeName,
         Products.price,
         Products.stock
ORDER BY Products.productID;

-- View: Animals browse data with availability converted to Yes/No.
CREATE OR REPLACE VIEW v_browse_animals_page AS
SELECT Animals.animalID AS "Animal ID",
       Animals.name AS "Name",
       Animals.species AS "Species",
       Animals.age AS "Age",
       Animals.price AS "Price",
       CASE WHEN Animals.isAvailable = 1 THEN 'Yes' ELSE 'No' END AS "Available",
       Animals.orderID AS "Order ID"
FROM Animals
ORDER BY Animals.animalID;

-- View: Product type browse data with products-using-type count.
CREATE OR REPLACE VIEW v_browse_product_types_page AS
SELECT ProductTypes.productTypeCode AS "Product Type Code",
       ProductTypes.productTypeName AS "Product Type Name",
       COUNT(Products.productID) AS "Products Using Type"
FROM ProductTypes
LEFT JOIN Products
       ON Products.productTypeCode = ProductTypes.productTypeCode
GROUP BY ProductTypes.productTypeCode,
         ProductTypes.productTypeName
ORDER BY ProductTypes.productTypeCode;

-- View: Employees browse data.
CREATE OR REPLACE VIEW v_browse_employees_page AS
SELECT Employees.employeeID AS "Employee ID",
       Employees.firstName AS "First Name",
       Employees.lastName AS "Last Name",
       Employees.jobTitle AS "Job Title"
FROM Employees
ORDER BY Employees.employeeID;

-- View: Employee assignments browse data with animal and employee names.
CREATE OR REPLACE VIEW v_browse_employee_assignments_page AS
SELECT EmployeeAnimals.animalDetailsID AS "Assignment ID",
       Animals.animalID AS "Animal ID",
       Animals.name AS "Animal Name",
       Animals.species AS "Species",
       Employees.employeeID AS "Employee ID",
       Employees.firstName AS "Employee First Name",
       Employees.lastName AS "Employee Last Name"
FROM EmployeeAnimals
LEFT JOIN Animals
       ON EmployeeAnimals.animalID = Animals.animalID
LEFT JOIN Employees
       ON EmployeeAnimals.employeeID = Employees.employeeID
ORDER BY EmployeeAnimals.animalDetailsID;
