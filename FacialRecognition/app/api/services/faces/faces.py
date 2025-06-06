from deepface import DeepFace
import faiss
import numpy as np
import mysql.connector
import os
from uuid import uuid4
from pathlib import Path
import base64
import faiss
import cv2
import time
from fastapi.responses import JSONResponse
from app.api.utils.iou import calculate_iou

IMAGE_PATH = "/app/app/api/temp/face_recognized.jpeg"
DB_PATH = "/app/faiss/face_index.index"
FAISS_SIZE = 2622
FAISS_DIR = Path(DB_PATH).parent
FAISS_DIR.mkdir(parents=True, exist_ok=True)

if os.path.exists(DB_PATH):
    index = faiss.read_index(DB_PATH)
else:
    index = faiss.IndexFlatL2(FAISS_SIZE)

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor(dictionary=True)

async def save_face_service(file, clerk_id: str):
    
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    print(result)
    print(clerk_id)
    
    if not result:
        return {"error": "User not found"}
    
    user_dict = {
            "id": result['id'],
            "name": result['name'],
            "clerk_id": result['clerk_id']
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
        
    face_id = str(uuid4())

    cursor.execute("""
        INSERT INTO face_embeddings (id, id_user, name, faiss_index_id, image_path, clerk_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (face_id, user_dict["id"], user_dict["name"], faiss_id, image_path, clerk_id))
    db.commit()

    return {"id": faiss_id}

async def get_faces_service(img_id):
    try:
        dir_path = f'/app/app/api/facesDatabase/{img_id}'
        
        if not os.path.exists(dir_path):
            return {"error": f"Directory for ID '{img_id}' not found."}

        imgs = os.listdir(dir_path)
        imgs = [img for img in imgs if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        encoded_imgs = []
        for img in imgs:
            img_path = os.path.join(dir_path, img)
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                encoded_imgs.append(encoded_string)

        return {"imgs": encoded_imgs}
    
    except Exception as e:
        return {"error": str(e)}

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

async def identify_face(file, modelName="VGG-Face"):
    contents = await file.read()
    with open(IMAGE_PATH, "wb") as f:
        f.write(contents)

    # Load index
    index = faiss.read_index(DB_PATH)
    results = []

    # Extract all faces
    faces = DeepFace.extract_faces(img_path=IMAGE_PATH, detector_backend='retinaface')
    img = cv2.imread(IMAGE_PATH)

    names = []
    base64_faces = []
    backups = []
    coords_seen = []

    for i, face in enumerate(faces):
        coords = [face["facial_area"]["x"], face["facial_area"]["y"], face["facial_area"]["w"], face["facial_area"]["h"]]

        # Avoid duplicate matches (IoU)
        if any(calculate_iou(coords, prev) > 0.35 for prev in coords_seen):
            continue
        coords_seen.append(coords)

        # Crop & represent
        face_crop = img[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
        embedding = DeepFace.represent(img_path=IMAGE_PATH, model_name=modelName, enforce_detection=False, detector_backend="retinaface")[i]['embedding']
        embedding_np = np.array(embedding).astype("float32").reshape(1, -1)

        # FAISS search
        D, I = index.search(embedding_np, 5)

        face_b64 = base64.b64encode(cv2.imencode('.jpg', face_crop)[1]).decode('utf-8')
        base64_faces.append(face_b64)

        # Fetch names for top results
        matched_names = []
        matched_clerk_ids = []
        for j, idx in enumerate(I[0]):
            cursor.execute("SELECT name, clerk_id FROM face_embeddings WHERE faiss_index_id = %s", (int(idx),))
            row = cursor.fetchone()
            if row:
                print(row)
                matched_names.append({"name": row["name"], "confidence": round(float(D[0][j]), 2)})
                matched_clerk_ids.append(row["clerk_id"])

        if matched_names:
            names.append([matched_names[0]["name"]])
            backups.append(matched_names[1:])  # other backup names
        else:
            names.append(f"No Match {i+1}")
            backups.append([{"name": "No Match", "confidence": 0.0}])

    return JSONResponse(content={
        "faces": base64_faces,
        "names": names,
        "backups": backups,
        "coords": coords_seen,
        "clerk_ids": matched_clerk_ids,
    })

    