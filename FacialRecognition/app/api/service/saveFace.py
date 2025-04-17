import os
import io
import base64
from app.api.DTO.FaceDataDTO import FaceData
from fastapi import HTTPException

# --------------------------------------- #

def save_face_service(data: FaceData):
    name = data.name.strip()
    image_base64 = data.image
    image = base64.b64decode(image_base64)
    contents = io.BytesIO(image).read()

    if not os.path.exists(f"/app/app/api/facesDatabase/{name}"):
        os.makedirs(f"/app/app/api/facesDatabase/{name}")

    imgName = f"{name} ({len(os.listdir(f'/app/app/api/facesDatabase/{name}'))+1})"
    with open(f"/app/app/api/facesDatabase/{name}/{imgName}.jpeg", "wb") as f:
        f.write(contents)

    return {"message": "Face saved successfully"}

# --------------------------------------- #

def add_name(name: str):
    with open('app/api/NOMES_PESSOAS.csv', 'a') as file:
        file.write(f'\n"{name},,",')
    return {"message": "Name added successfully"}

# --------------------------------------- #

async def service_revert_save_face(description: str):

    
    name = description.replace("Salvou uma face com o nome ", "")
    name = name.replace(" no sistema", "")
    name = name.strip()

    latest_image = sorted(os.listdir(f'/app/app/api/facesDatabase/{name}'))[-1]
    os.remove(f'/app/app/api/facesDatabase/{name}/{latest_image}')

    return {"message": "Face removed successfully"}
    
    