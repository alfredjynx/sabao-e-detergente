CREATE DATABASE IF NOT EXISTS bubble;
USE bubble;


CREATE TABLE face_embeddings (
    id uniqueidentifier NOT NULL DEFAULT newid(),
    name VARCHAR(255) NOT NULL,
    faiss_index_id INT NOT NULL,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clerk_id VARCHAR(255)
);
