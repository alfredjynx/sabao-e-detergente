from deepface import DeepFace
import faiss
import numpy as np
import os
from uuid import uuid4
from pathlib import Path
import base64
import faiss
import cv2
import time
from fastapi.responses import JSONResponse
from app.api.utils.iou import calculate_iou
from app.api.services.db import db, cursor

IMAGE_PATH = "/app/app/api/temp/face_recognized.jpeg"
DB_PATH = "/app/faiss/face_index.index"
FAISS_SIZE = 128  # Dlib embedding size
FAISS_DIR = Path(DB_PATH).parent
FAISS_DIR.mkdir(parents=True, exist_ok=True)

# Carregue o índice FAISS uma única vez ao iniciar o módulo
faiss_index = None
if os.path.exists(DB_PATH):
    print("DEBUG: Loading existing FAISS index from", DB_PATH)
    faiss_index = faiss.read_index(DB_PATH)
else:
    faiss_index = None  # Será criado na primeira gravação

# Log para mostrar os pesos disponíveis
print('Pesos DeepFace disponíveis em /root/.deepface/weights:', os.listdir('/root/.deepface/weights') if os.path.exists('/root/.deepface/weights') else 'Diretório não existe')

async def save_face_service(file, clerk_id: str):
    
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    print(result)
    print(clerk_id)
    
    if not result:
        return {"error": "User not found"}
    # result é uma tupla: (id, name, clerk_id)
    user_dict = {
        "id": result[0],
        "name": result[1],
        "clerk_id": result[2]
    }
    
    contents = await file.read()
    
    temp_path = "/app/app/api/temp/face_recognized.jpeg"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # Resize da imagem para acelerar processamento
    img = cv2.imread(temp_path)
    img_resized = cv2.resize(img, (160, 160))
    cv2.imwrite(temp_path, img_resized)

    # 1. Extract embedding usando Facenet e detector opencv
    embedding = DeepFace.represent(img_path=temp_path, model_name="Facenet", detector_backend="opencv")[0]['embedding']
    embedding_np = np.array(embedding).astype("float32")
    embedding_np = embedding_np / np.linalg.norm(embedding_np)  # Normalização L2
    embedding_np = embedding_np.reshape(1, -1)
    global faiss_index
    if faiss_index is not None:
        if embedding_np.shape[1] != faiss_index.d:
            print(f"[ERRO] Dimensão do embedding ({embedding_np.shape[1]}) diferente do índice FAISS ({faiss_index.d}). Resetando índice.")
            faiss_index = faiss.IndexFlatL2(embedding_np.shape[1])
            faiss.write_index(faiss_index, DB_PATH)
        index = faiss_index
    else:
        index = faiss.IndexFlatL2(embedding_np.shape[1])
        faiss_index = index

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
    global faiss_index
    if faiss_index is not None:
        faiss_index.remove_ids(np.array(faiss_ids, dtype=np.int64))
        faiss.write_index(faiss_index, DB_PATH)

    # Delete from MySQL
    cursor.execute("DELETE FROM face_embeddings WHERE clerk_id = %s", (clerk_id,))
    db.commit()

async def identify_face(file, modelName="Facenet"):
    contents = await file.read()
    with open(IMAGE_PATH, "wb") as f:
        f.write(contents)

    # Resize da imagem para acelerar processamento
    img = cv2.imread(IMAGE_PATH)
    img_resized = cv2.resize(img, (160, 160))
    cv2.imwrite(IMAGE_PATH, img_resized)

    global faiss_index
    if faiss_index is None:
        faiss_index = faiss.IndexFlatL2(128)  # Facenet embedding size
        faiss.write_index(faiss_index, DB_PATH)
    index = faiss_index

    # Usar detector opencv para evitar download de pesos
    try:
        faces = DeepFace.extract_faces(img_path=IMAGE_PATH, detector_backend='opencv')
        img = cv2.imread(IMAGE_PATH)
    
    except: 
        return JSONResponse(status_code=400, content={"error": "Nenhuma face detectada na imagem."})

    recognitions = []
    coords_seen = []

    for i, face in enumerate(faces):
        coords = [face["facial_area"]["x"], face["facial_area"]["y"], face["facial_area"]["w"], face["facial_area"]["h"]]
        if any(calculate_iou(coords, prev) > 0.35 for prev in coords_seen):
            continue
        coords_seen.append(coords)
        face_crop = img[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
        # Sempre usar Facenet e detector opencv
        embedding = DeepFace.represent(img_path=IMAGE_PATH, model_name="Facenet", enforce_detection=False, detector_backend="opencv")[i]['embedding']
        embedding_np = np.array(embedding).astype("float32")
        embedding_np = embedding_np / np.linalg.norm(embedding_np)  # Normalização L2
        embedding_np = embedding_np.reshape(1, -1)
        try:
            D, I = index.search(embedding_np, 5)
        except Exception as e:
            print(f"[ERRO] FAISS search falhou: {e}. Resetando índice.")
            faiss_index = faiss.IndexFlatL2(embedding_np.shape[1])
            faiss.write_index(faiss_index, DB_PATH)
            index = faiss_index
            D, I = index.search(embedding_np, 5)
        face_b64 = base64.b64encode(cv2.imencode('.jpg', face_crop)[1]).decode('utf-8')
        # Buscar apenas o match mais próximo
        best_idx = int(I[0][0])
        best_conf = float(D[0][0])
        cur = db.cursor()
        cur.execute("SELECT name, clerk_id FROM face_embeddings WHERE faiss_index_id = %s", (best_idx,))
        row = cur.fetchone()
        cur.fetchall()  # Garante que todos os resultados foram consumidos
        cur.close()
        if row and best_conf <= 0.8:
            recognition = {
                "name": row[0],
                "confidence": round(best_conf, 2),
                "coords": coords,
                "face": face_b64,
                "clerk_id": row[1]
            }
        else:
            recognition = {
                "name": "No Match",
                "confidence": round(best_conf, 2),
                "coords": coords,
                "face": face_b64,
                "clerk_id": None
            }
        recognitions.append(recognition)

    if not recognitions:
        return JSONResponse(status_code=200, content={"error": "Nenhuma face reconhecida na imagem."})

    return JSONResponse(content={
        "recognitions": recognitions
    })

