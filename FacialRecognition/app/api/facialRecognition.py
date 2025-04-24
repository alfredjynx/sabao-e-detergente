from fastapi import File, Form, UploadFile, APIRouter
import os

from app.api.DTO.FaceDataDTO import FaceData
from app.api.service.saveFace import save_face_service
from app.api.service.identifyFace import identify_face
from app.api.service.getNames import get_faces

# --------------------------------------- #

TEMP_FOLDER = '/app/app/api/temp'
FACE_DATABASE = '/app/app/api/facesDatabase'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
if not os.path.exists(FACE_DATABASE):
    os.makedirs(FACE_DATABASE)

# --------------------------------------- #

router = APIRouter()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.post("/face/facial-recognition/")
async def upload_image(
    file: UploadFile = File(...),
    modelName: str = Form("VGG-Face") 
):
    """Uploads an image and identifies the faces in it.
    Args:
        file (UploadFile): The image file to be uploaded.
        modelName (str): The name of the model to be used. Defaults to "VGG-Face".
    Returns:
        dict: Returns a dictionary with the following keys:
        "faces": A list of images of the faces found.
        "names": A list of the names of the faces found.
        "backups": A backup list of names in case the names were incorrect.

    """
    response = await identify_face(file, modelName)
    return response

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.post("/face/save-face/")
async def save_face(
    file: UploadFile = File(...),
    name: str = Form() 
):
    """Saves a face in the database.
    Args:
        data (FaceData): The data of the face to be saved. It must contain the following keys:
        "name": The name of the face.
        "image": The image of the face.
        "token": The token of the user making the request.
    Returns:
        dict: Returns a dictionary with "id" indicating uuid of person saved
    """
    response = await save_face_service(file, name)
    
    print(response)
    
    return response

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.get("/face/get-faces/")
async def router_get_names(
    img_id: str = Form() 
):
    """Gets the names of the faces in the database.
    Returns:
        dict: Returns a dictionary with the key "names" containing a list of the names of all possible names.
    """
    response = get_faces(img_id)
    return response


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

