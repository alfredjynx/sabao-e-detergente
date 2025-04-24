from deepface import DeepFace
import faiss
import numpy as np
import mysql.connector
import os
from uuid import uuid4
from pathlib import Path

DB_PATH = "/app/faiss/face_index.index"
FAISS_SIZE = 2622  # VGG-Face
FAISS_DIR = Path(DB_PATH).parent
FAISS_DIR.mkdir(parents=True, exist_ok=True)

# Load or create FAISS index
if os.path.exists(DB_PATH):
    index = faiss.read_index(DB_PATH)
else:
    index = faiss.IndexFlatL2(FAISS_SIZE)

# MySQL connection (customize credentials via env or use a shared util)
db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor()

# ------------------------------ #

async def save_face_service(file, name: str):
    contents = await file.read()
    
    temp_path = "/app/app/api/temp/face_recognized.jpeg"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # 1. Extract embedding
    embedding = DeepFace.represent(img_path=temp_path, model_name="VGG-Face")[0]['embedding']
    embedding_np = np.array(embedding).astype("float32").reshape(1, -1)
    
    if os.path.exists(DB_PATH):
        index = faiss.read_index(DB_PATH)
        if embedding_np.shape[1] != index.d:
            raise ValueError(f"Embedding size {embedding_np.shape[1]} does not match FAISS index size {index.d}")
    else:
        index = faiss.IndexFlatL2(embedding_np.shape[1])

    # 2. Add to FAISS
    index.add(embedding_np)
    faiss.write_index(index, DB_PATH)
    faiss_id = index.ntotal - 1

    # 3. Save to MySQL
    image_path = f"/app/app/api/facesDatabase/{name}_{str(uuid4())[:8]}.jpeg"
    with open(image_path, "wb") as f:
        f.write(contents)

    cursor.execute("""
        INSERT INTO face_embeddings (name, faiss_index_id, image_path)
        VALUES (%s, %s, %s)
    """, (name, faiss_id, image_path))
    db.commit()

    return {"id": faiss_id}
