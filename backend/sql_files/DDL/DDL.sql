/*
Group 73
Members: Gage Cox
         Brandon Connely
         Carlos Chirinos
*/

START TRANSACTION;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS EmployeeAnimals;
DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Animals;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS ProductTypes;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Customers;

SET FOREIGN_KEY_CHECKS = 1;
SET AUTOCOMMIT=0;

-- Customers Table
-- Records information about customers who purchase products or animals from the store.
CREATE TABLE Customers (
    customerID int NOT NULL AUTO_INCREMENT,
    firstName varchar(50) NOT NULL,
    lastName varchar(50) NOT NULL,
    email varchar(50) UNIQUE NOT NULL,
    phoneNumber varchar(20) UNIQUE NOT NULL,
    PRIMARY KEY (customerID)
);

-- Employees Table
-- Represents a single employee, the transactions they make, and the animals they take care of
CREATE TABLE Employees (
    employeeID int NOT NULL AUTO_INCREMENT,
    firstName varchar(50) NOT NULL,
    lastName varchar(50) NOT NULL,
    jobTitle varchar(100) NOT NULL,
    PRIMARY KEY (employeeID)
);

-- Orders Table
-- Represents a transaction made by a customer. An order may include both products and animals of any quantity. 
CREATE TABLE Orders (
    orderID int NOT NULL AUTO_INCREMENT,
    orderDate date NOT NULL,
    orderTotal decimal(10,2) NOT NULL,
    customerID int,
    employeeID int,
    PRIMARY KEY (orderID),
    FOREIGN KEY (customerID) REFERENCES Customers(customerID) ON DELETE CASCADE,
    FOREIGN KEY (employeeID) REFERENCES Employees(employeeID) ON DELETE SET NULL
);

-- ProductTypes Table
-- Definition table for product types to prevent redundancy.
CREATE TABLE ProductTypes (
    productTypeCode varchar(50) NOT NULL,
    productTypeName varchar(50) NOT NULL,
    PRIMARY KEY (productTypeCode)
);

-- Products Table
-- Represents non-living products sold in store.
CREATE TABLE Products (
    productID int NOT NULL AUTO_INCREMENT,
    productName varchar(50) NOT NULL,
    productTypeCode varchar(50) NOT NULL,
    price decimal(10,2) NOT NULL,
    stock int NOT NULL,
    PRIMARY KEY (productID),
    FOREIGN KEY (productTypeCode) REFERENCES ProductTypes(productTypeCode)
);

-- Animals Table
-- Represents a singular individual animal
CREATE TABLE Animals (
    animalID int NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    species varchar(100) NOT NULL,
    age int NOT NULL,
    price decimal(10,2) NOT NULL,
    isAvailable tinyint(1) NOT NULL,
    orderID int,
    PRIMARY KEY (animalID),
    FOREIGN KEY (orderID) REFERENCES Orders(orderID) ON DELETE CASCADE
);

-- Intersection of Orders and Products
CREATE TABLE OrderDetails (
    orderDetailsID int NOT NULL AUTO_INCREMENT,
    orderID int NOT NULL,
    productID int NOT NULL,
    quantity int NOT NULL,
    unitPrice decimal(10,2) NOT NULL,
    PRIMARY KEY (orderDetailsID),
    FOREIGN KEY (orderID) REFERENCES Orders(orderID) ON DELETE CASCADE,
    FOREIGN KEY (productID) REFERENCES Products(productID) ON DELETE CASCADE
);

-- Intersection of Animals and Employees
CREATE TABLE EmployeeAnimals (
    animalDetailsID int NOT NULL AUTO_INCREMENT,
    animalID int NOT NULL,
    employeeID int,
    PRIMARY KEY (animalDetailsID),
    FOREIGN KEY (animalID) REFERENCES Animals(animalID) ON DELETE CASCADE,
    FOREIGN KEY (employeeID) REFERENCES Employees(employeeID) ON DELETE SET NULL
);

/*
Example Data Inserts
*/


-- Customers
INSERT INTO Customers (firstName, lastName, email, phoneNumber)
VALUES ('Alex', 'Rivera', 'alex.rivera@email.com', '541-555-0101'),
('Jamie', 'Chen', 'jamie.chen@email.com', '541-555-0102'),
('Morgan', 'Patel', 'morgan.patel@email.com', '541-555-0103');

-- ProductTypes
INSERT INTO ProductTypes (productTypeCode, productTypeName)
VALUES ('ENC', 'Enclosure'),
('LGT', 'Lighting'),
('FOD', 'Food');

-- Products
INSERT INTO Products (productName, productTypeCode, price, stock)
VALUES ('40-Gallon Terrarium', 'ENC', 199.99, 10),
('Heat Lamp', 'LGT', 29.99, 25),
('Calcium Supplement', 'FOD', 9.99, 50);

-- Employees
INSERT INTO Employees (firstName, lastName, jobTitle)
VALUES ('Taylor', 'Morgan', 'Store Manager'),
('Jordan', 'Lee', 'Animal Care Specialist'),
('Casey', 'Smith', 'Sales Associate');

-- Orders
INSERT INTO Orders (orderDate, orderTotal, customerID, employeeID)
VALUES ('2026-01-15', 239.97, 1, 3),
('2026-01-18', 59.98, 2, 3),
('2026-01-20', 229.96, 1, 1);

-- Animals (UPDATED WITH NAMES)
INSERT INTO Animals (name, species, age, price, isAvailable, orderID)
VALUES 
('Lacey', 'Leopard Gecko', 2, 149.99, 0, 1),
('Spike', 'Bearded Dragon', 1, 199.99, 0, 3),
('Sly', 'Corn Snake', 3, 129.99, 1, NULL);

-- OrderDetails
INSERT INTO OrderDetails (orderID, productID, quantity, unitPrice)
VALUES (1, 1, 1, 199.99),
(1, 2, 1, 29.99),
(1, 3, 1, 9.99),
(2, 2, 2, 29.99),
(3, 1, 1, 199.99),
(3, 3, 3, 9.99);

-- EmployeeAnimals
INSERT INTO EmployeeAnimals (animalID, employeeID)
VALUES (1, (SELECT employeeID FROM Employees WHERE jobTitle = 'Animal Care Specialist')),
(2, (SELECT employeeID FROM Employees WHERE jobTitle = 'Animal Care Specialist')),
(3, (SELECT employeeID FROM Employees WHERE jobTitle = 'Animal Care Specialist'));

SET FOREIGN_KEY_CHECKS=1;
COMMIT;