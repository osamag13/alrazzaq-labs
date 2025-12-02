-- Create a sample database
CREATE DATABASE IF NOT EXISTS sampleapp;

-- Use the database
USE sampleapp;

-- Create a users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email) VALUES
('john_doe', 'john@example.com'),
('jane_smith', 'jane@example.com'),
('docker_user', 'docker@compose.com');

-- Create a simple view
CREATE VIEW user_count AS
SELECT COUNT(*) as total_users FROM users;
