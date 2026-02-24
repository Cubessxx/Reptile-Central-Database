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
