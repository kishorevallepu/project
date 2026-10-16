CREATE TABLE IF NOT EXISTS assessment_results (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    realistic_score TINYINT UNSIGNED NOT NULL,
    investigative_score TINYINT UNSIGNED NOT NULL,
    artistic_score TINYINT UNSIGNED NOT NULL,
    social_score TINYINT UNSIGNED NOT NULL,
    enterprising_score TINYINT UNSIGNED NOT NULL,
    conventional_score TINYINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_assessment_results_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    subject VARCHAR(160) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS course_catalog (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    riasec_type CHAR(1) NOT NULL,
    category_name VARCHAR(40) NOT NULL,
    category_description VARCHAR(255) NOT NULL,
    name VARCHAR(120) NOT NULL,
    icon VARCHAR(60) NOT NULL,
    level VARCHAR(80) NOT NULL,
    duration VARCHAR(60) NOT NULL,
    description TEXT NOT NULL,
    display_order TINYINT UNSIGNED NOT NULL DEFAULT 0,
    UNIQUE KEY uq_course_catalog_type_name (riasec_type, name),
    INDEX idx_course_catalog_type_order (riasec_type, display_order)
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_password_reset_user_expiry (user_id, expires_at)
);