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

async def delete_face_service(clerk_id: str):
    
    cursor.execute("SELECT * FROM face_embeddings WHERE clerk_id = %s", (clerk_id,))
    results = cursor.fetchone()
    
    if not results:
        return {"error": "User not found"}
    
    # Extract FAISS index IDs
    faiss_ids = [row[2] for row in results]  # index 2 = faiss_index_id

    # Remove from FAISS
    index.remove_ids(np.array(faiss_ids, dtype=np.int64))

    # Delete from MySQL
    cursor.execute("DELETE FROM face_embeddings WHERE clerk_id = %s", (clerk_id,))
    db.commit()
    
    
    