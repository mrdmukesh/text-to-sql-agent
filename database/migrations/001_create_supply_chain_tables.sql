-- Supply Chain Operations Database

DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_type VARCHAR(50),
    city VARCHAR(50),
    country VARCHAR(50),
    created_date DATE
);

CREATE TABLE warehouses (
    warehouse_id INT PRIMARY KEY,
    warehouse_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    capacity INT
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    unit_price DECIMAL(10,2)
);

CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY,
    warehouse_id INT,
    product_id INT,
    stock_quantity INT,
    reorder_level INT,
    last_updated DATE
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    order_status VARCHAR(50),
    priority VARCHAR(20)
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2)
);

CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY,
    order_id INT,
    warehouse_id INT,
    shipment_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    carrier VARCHAR(50),
    shipment_status VARCHAR(50)
);

CREATE TABLE invoices (
    invoice_id INT PRIMARY KEY,
    order_id INT,
    invoice_date DATE,
    invoice_amount DECIMAL(12,2),
    invoice_status VARCHAR(50)
);

CREATE TABLE payments (
    payment_id INT PRIMARY KEY,
    invoice_id INT,
    payment_date DATE,
    payment_amount DECIMAL(12,2),
    payment_status VARCHAR(50)
);

CREATE TABLE claims (
    claim_id INT PRIMARY KEY,
    order_id INT,
    customer_id INT,
    claim_date DATE,
    claim_type VARCHAR(50),
    claim_amount DECIMAL(12,2),
    claim_status VARCHAR(50)
);

CREATE TABLE support_tickets (
    ticket_id INT PRIMARY KEY,
    customer_id INT,
    order_id INT,
    ticket_date DATE,
    issue_type VARCHAR(50),
    priority VARCHAR(20),
    ticket_status VARCHAR(50)
);