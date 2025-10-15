-- Use your database
CREATE DATABASE IF NOT EXISTS logistics_db;
USE logistics_db;

-- -----------------------------
-- Table: user
-- -----------------------------
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    mobile VARCHAR(20) UNIQUE,
    password VARCHAR(200) NOT NULL,
    user_type VARCHAR(20) NOT NULL,      -- 'individual' or 'business'
    business_doc VARCHAR(200) NULL
);

-- -----------------------------
-- Table: shipment
-- -----------------------------
CREATE TABLE shipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_id VARCHAR(20) UNIQUE,
    sender VARCHAR(100) NOT NULL,
    receiver VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    weight FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
SHOW TABLES;
select * from shipment;
ALTER TABLE shipment
ADD COLUMN receiver_mobile VARCHAR(20) AFTER receiver,
ADD COLUMN address_line1 VARCHAR(255) AFTER origin,
ADD COLUMN address_line2 VARCHAR(255) AFTER address_line1;

select * from user;

ALTER TABLE shipment
ADD COLUMN pincode long AFTER address_line2,
ADD COLUMN state VARCHAR(255) AFTER pincode;
ALTER TABLE shipment
add column country varchar(255) after state;

select * from shipment;
alter table shipment
add column d_address_line1 varchar(225) after country,
add column d_address_line2 varchar(225) after d_address_line1,
add column d_pincode long after d_address_line2,
add column d_state varchar(225) after d_pincode,
add column d_country varchar(225) after d_state;

