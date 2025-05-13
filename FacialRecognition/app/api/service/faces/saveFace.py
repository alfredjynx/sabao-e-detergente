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
    faiss.write_index(index, DB_PATH)

# MySQL connection (customize credentials via env or use a shared util)
db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor()

# ------------------------------ #

async def save_face_service(file, clerk_id: str):
    
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    print(result)
    print(clerk_id)
    
    if not result:
        return {"error": "User not found"}
    
    user_dict = {
            "id": result[0],
            "name": result[1],
            "clerk_id": result[2]
        }
    
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
    
    if not os.path.exists(f"/app/app/api/facesDatabase/{faiss_id}"):
        os.mkdir(f"/app/app/api/facesDatabase/{faiss_id}")
    
    image_path = f"/app/app/api/facesDatabase/{faiss_id}/{user_dict['name']}_{str(uuid4())[:8]}.jpeg"
    with open(image_path, "wb") as f:
        f.write(contents)

    cursor.execute("""
        INSERT INTO face_embeddings (id, name, faiss_index_id, image_path, clerk_id)
        VALUES (%s, %s, %s, %s, %s)
    """, ( user_dict["id"], user_dict["name"], faiss_id, image_path, clerk_id))
    db.commit()

    return {"id": faiss_id}
