-- ============================================================
-- Billing System — Phase 1 Database Schema
-- Run this in MySQL Workbench or phpMyAdmin
-- ============================================================

CREATE DATABASE IF NOT EXISTS billing_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE billing_system;

-- ── Users (Login & Auth) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,   -- Werkzeug hashed
    role        ENUM('admin','manager','cashier') NOT NULL DEFAULT 'cashier',
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    last_login  DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Activity Log ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    action      VARCHAR(255),
    ip_address  VARCHAR(45),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ── Login Attempts (for lockout) ─────────────────────────
CREATE TABLE IF NOT EXISTS login_attempts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50),
    ip_address  VARCHAR(45),
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Settings (key-value store) ───────────────────────────
CREATE TABLE IF NOT EXISTS settings (
    setting_key   VARCHAR(100) PRIMARY KEY,
    setting_value TEXT,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── Default Settings ──────────────────────────────────────
INSERT IGNORE INTO settings (setting_key, setting_value) VALUES
('shop_name',    'My Billing System'),
('shop_address', '123 Main Street, City'),
('shop_phone',   '9876543210'),
('shop_email',   'shop@example.com'),
('shop_gstin',   '22AAAAA0000A1Z5'),
('currency',     '₹'),
('app_version',  '1.0.0');

-- ── Default Admin User ────────────────────────────────────
-- Password: admin@123  (change after first login!)
INSERT IGNORE INTO users (full_name, username, password, role) VALUES
('Administrator', 'admin',
 'scrypt:32768:8:1$sHMnhHqNc6BNKGZG$3f5c8c3e1d0f7b9c3d5e7f9b1d3f5c7e9b1d3f5c7e9b1d3f5c7e9b1d3f5c7e9b1d3f5c7e9b1d3f5c7e9b',
 'admin');

-- NOTE: The password hash above is a placeholder. The app will
-- handle hashing via Werkzeug on first run using the seed script.
