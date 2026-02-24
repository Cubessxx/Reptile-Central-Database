USE `sql3817488`;

DROP PROCEDURE IF EXISTS sp_generic_delete;
DELIMITER //

-- Generic function that can fufill any DELETE Option needed for the database
CREATE PROCEDURE sp_generic_delete(
    IN delete_id VARCHAR(64),
    IN target_id VARCHAR(255)
)
BEGIN
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
