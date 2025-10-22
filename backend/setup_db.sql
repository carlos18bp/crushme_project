CREATE DATABASE IF NOT EXISTS crushme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'crushme_user'@'localhost' IDENTIFIED BY 'CrushM3_S3cur3_P@ss2025!';
GRANT ALL PRIVILEGES ON crushme.* TO 'crushme_user'@'localhost';
FLUSH PRIVILEGES;
