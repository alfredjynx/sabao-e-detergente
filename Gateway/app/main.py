from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests

# --------------------------------------- #

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@app.get("/")
def root():
    return {"Hello": "World, Gateway"}
    
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #


@app.post("/face/facial-recognition/")
async def create_upload_file(
    file: UploadFile | None = None, 
    modelName: str = Form("VGG-Face")
):
    try:
                
        url = "http://facial-recognition:8000" + "/face/facial-recognition/"
        files = {"file": (file.filename, file.file, file.content_type)}
        data = {
            "modelName": modelName
        }

        response = requests.post(url, files=files, data=data)
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}
        
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@app.post("/face/save-face/")
async def create_upload_file(
    data: dict
):
    try:
                
        url = "http://facial-recognition:8000" + "/face/save-face/"
        
        response = requests.post(url, json=data)
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}
    
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@app.get("/face/get-names/")
async def create_upload_file():
    try:
                
        url = "http://facial-recognition:8000" + "/face/get-names/"
        
        response = requests.get(url)
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}
    
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@app.post("/face/add-name/")
async def create_upload_file(
    data: dict
):
    try:
                
        url = "http://facial-recognition:8000" + "/face/add-name/"
        
        response = requests.post(url, json=data)
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}
    
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@app.post("/face/revert-save-face/")
async def create_upload_file(
    data: dict
):
    try:
                
        url = "http://facial-recognition:8000" + "/face/revert-save-face/"
        
        response = requests.post(url, json=data)
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}
    
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #