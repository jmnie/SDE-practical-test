/*
Explaination：

1. sellers table: store the information of the sellers
   - rating, status to manage the seller's status 
   - created_at, updated_at, timestamps 

2. categories table: store the category of the items 
   - parent_id: 
   - status: active, inactive
   - display_order: to manage the display order of the categories

3. offers table: the goods table 
   - status: field for item state management
   - tracking metrics: (view_count, sale_count) for engagement statistics 
   - rank_score: field for sorting algorithm implementation
   - optimized indices: for improved query performance
*/

-- seller table 
CREATE TABLE sellers (
    seller_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0.00,  -- rating for the seller 
    total_offers INT DEFAULT 0,       
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_seller_status (status),
    INDEX idx_seller_rating (rating)
);

-- category table 
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NULL,                
    name VARCHAR(255) NOT NULL,
    display_order INT DEFAULT 0,      
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id),
    INDEX idx_category_parent (parent_id),
    INDEX idx_category_status (status)
);

-- offers table 
CREATE TABLE offers (
    offer_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    status ENUM('active', 'inactive', 'sold', 'suspended') DEFAULT 'active',
    view_count INT DEFAULT 0,          
    sale_count INT DEFAULT 0,         
    rank_score DECIMAL(10,4) DEFAULT 0.0000,  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_offer_status (status),
    INDEX idx_offer_category (category_id, status),  -- category selection
    INDEX idx_offer_seller (seller_id, status),      -- seller selection 
    INDEX idx_offer_rank (category_id, status, rank_score)  -- optimize the rank
);

-- Trigger: update when the offer is traded 
DELIMITER //
CREATE TRIGGER after_offer_insert
AFTER INSERT ON offers
FOR EACH ROW
BEGIN
    UPDATE sellers 
    SET total_offers = total_offers + 1
    WHERE seller_id = NEW.seller_id;
END;//

CREATE TRIGGER after_offer_delete
AFTER DELETE ON offers
FOR EACH ROW
BEGIN
    UPDATE sellers 
    SET total_offers = total_offers - 1
    WHERE seller_id = OLD.seller_id;
END;//
DELIMITER ;

-- query the goods 
CREATE VIEW v_category_offers AS
SELECT 
    o.*,
    s.name as seller_name,
    s.rating as seller_rating,
    ROW_NUMBER() OVER (
        PARTITION BY o.seller_id 
        ORDER BY o.rank_score DESC
    ) as seller_offer_rank
FROM offers o
JOIN sellers s ON o.seller_id = s.seller_id
WHERE o.status = 'active'
ORDER BY seller_offer_rank, o.seller_id;