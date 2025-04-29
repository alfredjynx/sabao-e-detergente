import faiss
import numpy as np
import base64
import mysql.connector
import cv2
import time
from deepface import DeepFace
from fastapi.responses import JSONResponse

DB_PATH = "/app/faiss/face_index.index"
IMAGE_PATH = "/app/app/api/temp/face_recognized.jpeg"

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor(dictionary=True)

def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    x_inter1 = max(x1, x2)
    y_inter1 = max(y1, y2)
    x_inter2 = min(x1 + w1, x2 + w2)
    y_inter2 = min(y1 + h1, y2 + h2)
    inter_width = max(0, x_inter2 - x_inter1)
    inter_height = max(0, y_inter2 - y_inter1)
    intersection_area = inter_width * inter_height
    union_area = w1 * h1 + w2 * h2 - intersection_area
    return intersection_area / union_area if union_area != 0 else 0


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
        for j, idx in enumerate(I[0]):
            cursor.execute("SELECT name FROM face_embeddings WHERE faiss_index_id = %s", (int(idx),))
            row = cursor.fetchone()
            if row:
                matched_names.append({"name": row["name"], "confidence": round(float(D[0][j]), 2)})

        if matched_names:
            names.append(matched_names[0]["name"])
            backups.append(matched_names[1:])  # other backup names
        else:
            names.append(f"No Match {i+1}")
            backups.append([{"name": "No Match", "confidence": 0.0}])

    return JSONResponse(content={
        "faces": base64_faces,
        "names": names,
        "backups": backups,
        "coords": coords_seen
    })
