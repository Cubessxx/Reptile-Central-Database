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
