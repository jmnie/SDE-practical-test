/*
  Here are 3 tables for this question:
  1. customers  
    the table for store the information about the customer, name, email, create_time and update_time
  2. orders 
    record for each order, like unique order identifier, reference to the customer, order status, date the order was created 
  3. reward_points
    This table tracks the reward points awarded to customers. It contains a unique identifier for each reward entry and update time. 
*/

-- Table: customers
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: orders
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status ENUM('Pending', 'Delivered', 'Cancelled') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Table: reward_points
CREATE TABLE reward_points (
    point_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    points INT NOT NULL,
    expiry_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
