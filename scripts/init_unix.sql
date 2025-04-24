CREATE DATABASE IF NOT EXISTS bubble;
USE bubble;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    admin BOOLEAN DEFAULT FALSE,
    canPay BOOLEAN DEFAULT FALSE,
    canFace BOOLEAN DEFAULT FALSE,
    canTrain BOOLEAN DEFAULT FALSE,
    confirmation_token VARCHAR(255),
    token_expires_at DATETIME,
    disabled BOOLEAN DEFAULT FALSE,
    INDEX idx_username (username)
);


CREATE TABLE face_embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    faiss_index_id INT NOT NULL,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (username, hashed_password, admin, canPay, canFace, canTrain, disabled, confirmation_token, token_expires_at)
VALUES ("admin", "unactivated", True, True, True, True, False, "1234", NOW() + INTERVAL 1 DAY);

INSERT INTO history (user_id, action, description, timestamp)
VALUES (1, "create", "User admin created", NOW());
