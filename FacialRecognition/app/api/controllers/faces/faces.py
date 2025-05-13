from fastapi import File, Form, UploadFile, APIRouter
import os

from app.api.services.faces.faces import *


TEMP_FOLDER = '/app/app/api/temp'
FACE_DATABASE = '/app/app/api/facesDatabase'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
if not os.path.exists(FACE_DATABASE):
    os.makedirs(FACE_DATABASE)


router = APIRouter()

@router.post("/faces/recognition")
async def upload_image(
    file: UploadFile = File(...),
    modelName: str = Form("VGG-Face") 
):
    response = await identify_face(file, modelName)
    return response

@router.post("/faces")
async def save_face(
    file: UploadFile = File(...),
    clerk_id: str = Form()
):
    response = await save_face_service(file, clerk_id=clerk_id)
    return response

@router.get("/faces")
async def router_get_names(
    img_id: str = Form() 
):
    response = get_faces_service(img_id)
    return response



