CREATE DATABASE IF NOT EXISTS bubble;
USE bubble;

CREATE TABLE face_embeddings (
    id CHAR(36) NOT NULL PRIMARY KEY,
    id_user CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    faiss_index_id INT NOT NULL,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clerk_id VARCHAR(255)
);

CREATE TABLE users (
    id CHAR(36) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    clerk_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE user_follow (
    id CHAR(36) NOT NULL PRIMARY KEY,
    id_follow CHAR(36) NOT NULL,
    id_followed CHAR(36) NOT NULL
);

CREATE TABLE messages (
    id CHAR(36) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);