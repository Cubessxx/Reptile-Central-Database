-- create.sql
USE `sql3817488`;

DROP PROCEDURE IF EXISTS sp_generic_create;
DELIMITER //

-- Generic function that can fufill any CREATE Option needed for the database
CREATE PROCEDURE sp_generic_create(
    IN create_id VARCHAR(64),
    IN p1 VARCHAR(255),
    IN p2 VARCHAR(255),
    IN p3 VARCHAR(255),
    IN p4 VARCHAR(255)
)
BEGIN
    -- Friendly SQL errors for common constraint failures.
    DECLARE EXIT HANDLER FOR 1062
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Duplicate value violates a unique constraint.';
    END;

    DECLARE EXIT HANDLER FOR 1451
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Cannot delete this item as a constraint prevents you from doing so.';
    END;

    DECLARE EXIT HANDLER FOR 1452
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Invalid reference. A related record was not found.';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Unknown SQL Error. Please refresh the page and try again.';
    END;

    CASE create_id

        -- Route: Customers.
        WHEN 'Customer' THEN
            INSERT INTO Customers (firstName, lastName, email, phoneNumber)
            VALUES (p1, p2, p3, p4);

        -- Route: Employees.
        WHEN 'Employee' THEN
            INSERT INTO Employees (firstName, lastName, jobTitle)
            VALUES (p1, p2, p3);

        -- Route: Product types.
        WHEN 'Product Type' THEN
            INSERT INTO ProductTypes (productTypeCode, productTypeName)
            VALUES (p1, p2);

        -- Route: Animals ( Assume default isAvailable=1 and orderID=NULL)
        WHEN 'Animal' THEN
            INSERT INTO Animals (name, species, age, price, isAvailable, orderID)
            VALUES (
                p1,
                p2,
                CAST(p3 AS UNSIGNED INTEGER),
                CAST(p4 AS DECIMAL(10,2)),
                1,
                NULL
            );

        -- Route: Products.
        WHEN 'Product' THEN
            INSERT INTO Products (productName, productTypeCode, price, stock)
            VALUES (
                p1,
                p2,
                CAST(p3 AS DECIMAL(10,2)),
                CAST(p4 AS UNSIGNED INTEGER)
            );

        -- Route: Employee assignments.
        WHEN 'Employee Assignment' THEN
            INSERT INTO EmployeeAnimals (animalID, employeeID)
            VALUES (
                CAST(p1 AS UNSIGNED INTEGER),
                CAST(p2 AS UNSIGNED INTEGER)
            );

        -- Route: Orders with current date and starting orderTotal.
        WHEN 'Order' THEN
            INSERT INTO Orders (orderDate, orderTotal, customerID, employeeID)
            VALUES (
                CURDATE(),
                0.00,
                CAST(p1 AS UNSIGNED INTEGER),
                CAST(p2 AS UNSIGNED INTEGER)
            );

            SELECT LAST_INSERT_ID() AS orderID;

        ELSE
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unsupported create_id passed to sp_generic_create.';
    END CASE;
END //

DELIMITER ;

-- read.sql
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

-- update.sql
USE `sql3817488`;

DROP PROCEDURE IF EXISTS sp_generic_update;
DELIMITER //

-- Generic function that can fufill any UPDATE Option needed for the database
CREATE PROCEDURE sp_generic_update(
    IN update_id VARCHAR(64),
    IN target_id VARCHAR(255),
    IN p1 VARCHAR(255),
    IN p2 VARCHAR(255),
    IN p3 VARCHAR(255),
    IN p4 VARCHAR(255)
)
BEGIN
    -- Friendly SQL errors for common constraint failures.
    DECLARE EXIT HANDLER FOR 1062
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Duplicate value violates a unique constraint.';
    END;

    DECLARE EXIT HANDLER FOR 1451
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Cannot delete this item as a constraint prevents you from doing so.';
    END;

    DECLARE EXIT HANDLER FOR 1452
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Invalid reference. A related record was not found.';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Unknown SQL Error. Please refresh the page and try again.';
    END;

    CASE update_id

        -- Route: Customers.
        WHEN 'Customer' THEN
            UPDATE Customers
            SET Customers.email = p1,
                Customers.phoneNumber = p2
            WHERE Customers.customerID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Employees.
        WHEN 'Employee' THEN
            UPDATE Employees
            SET Employees.firstName = p1,
                Employees.lastName = p2,
                Employees.jobTitle = p3
            WHERE Employees.employeeID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Product types.
        WHEN 'Product Type' THEN
            UPDATE ProductTypes
            SET ProductTypes.productTypeName = p1
            WHERE ProductTypes.productTypeCode = target_id;

        -- Route: Animals.
        WHEN 'Animal' THEN
            UPDATE Animals
            SET Animals.age = CAST(p1 AS UNSIGNED INTEGER),
                Animals.price = CAST(p2 AS DECIMAL(10,2)),
                Animals.isAvailable = CASE
                    WHEN p3 = 'Yes' THEN 1
                    ELSE 0
                END
            WHERE Animals.animalID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Products.
        WHEN 'Product' THEN
            UPDATE Products
            SET Products.productName = p1,
                Products.productTypeCode = p2,
                Products.price = CAST(p3 AS DECIMAL(10,2)),
                Products.stock = CAST(p4 AS UNSIGNED INTEGER)
            WHERE Products.productID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Employee assignments.
        WHEN 'Employee Assignment' THEN
            UPDATE EmployeeAnimals
            SET EmployeeAnimals.animalID = CAST(p1 AS UNSIGNED INTEGER),
                EmployeeAnimals.employeeID = CAST(p2 AS UNSIGNED INTEGER)
            WHERE EmployeeAnimals.animalDetailsID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Order detail  and order total recalculation.
        WHEN 'Order Detail' THEN
            IF EXISTS (
                SELECT 1
                FROM OrderDetails
                WHERE OrderDetails.orderID = CAST(target_id AS UNSIGNED INTEGER)
                  AND OrderDetails.productID = CAST(p1 AS UNSIGNED INTEGER)
            ) THEN
                UPDATE OrderDetails
                SET OrderDetails.quantity = CAST(p2 AS UNSIGNED INTEGER),
                    OrderDetails.unitPrice = (
                        SELECT Products.price
                        FROM Products
                        WHERE Products.productID = CAST(p1 AS UNSIGNED INTEGER)
                    )
                WHERE OrderDetails.orderID = CAST(target_id AS UNSIGNED INTEGER)
                  AND OrderDetails.productID = CAST(p1 AS UNSIGNED INTEGER);
            ELSE
                INSERT INTO OrderDetails (orderID, productID, quantity, unitPrice)
                VALUES (
                    CAST(target_id AS UNSIGNED INTEGER),
                    CAST(p1 AS UNSIGNED INTEGER),
                    CAST(p2 AS UNSIGNED INTEGER),
                    (
                        SELECT Products.price
                        FROM Products
                        WHERE Products.productID = CAST(p1 AS UNSIGNED INTEGER)
                    )
                );
            END IF;

            UPDATE Orders
            SET Orders.orderTotal = (
                SELECT COALESCE(SUM(OrderDetails.quantity * OrderDetails.unitPrice), 0.00)
                FROM OrderDetails
                WHERE OrderDetails.orderID = CAST(target_id AS UNSIGNED INTEGER)
            )
            WHERE Orders.orderID = CAST(target_id AS UNSIGNED INTEGER);

        ELSE
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unsupported update_id passed to sp_generic_update.';
    END CASE;
END //

DELIMITER ;

-- delete.sql
USE `sql3817488`;

DROP PROCEDURE IF EXISTS sp_generic_delete;
DELIMITER //

-- Generic function that can fufill any DELETE Option needed for the database
CREATE PROCEDURE sp_generic_delete(
    IN delete_id VARCHAR(64),
    IN target_id VARCHAR(255)
)
BEGIN
    -- Friendly SQL errors for common constraint failures.
    DECLARE EXIT HANDLER FOR 1062
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Duplicate value violates a unique constraint.';
    END;

    DECLARE EXIT HANDLER FOR 1451
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Cannot delete this item as a constraint prevents you from doing so.';
    END;

    DECLARE EXIT HANDLER FOR 1452
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Invalid reference. A related record was not found.';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'SQL ERROR: Unknown SQL Error. Please refresh the page and try again.';
    END;

    CASE delete_id

        -- Route: Customers.
        WHEN 'Customer ID' THEN
            DELETE FROM Customers
            WHERE Customers.customerID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Orders.
        WHEN 'Order ID' THEN
            DELETE FROM Orders
            WHERE Orders.orderID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Products.
        WHEN 'Product ID' THEN
            DELETE FROM Products
            WHERE Products.productID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Animals.
        WHEN 'Animal ID' THEN
            DELETE FROM Animals
            WHERE Animals.animalID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Employees.
        WHEN 'Employee ID' THEN
            DELETE FROM Employees
            WHERE Employees.employeeID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Employee assignments.
        WHEN 'Assignment ID' THEN
            DELETE FROM EmployeeAnimals
            WHERE EmployeeAnimals.animalDetailsID = CAST(target_id AS UNSIGNED INTEGER);

        -- Route: Product types.
        WHEN 'Product Type Code' THEN
            DELETE FROM ProductTypes
            WHERE ProductTypes.productTypeCode = target_id;

        ELSE
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unsupported delete_id passed to sp_generic_delete.';
    END CASE;
END //

DELIMITER ;
