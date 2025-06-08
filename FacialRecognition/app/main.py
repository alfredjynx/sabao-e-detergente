from app.api.controllers.faces import faces
from fastapi import FastAPI
from app.api.controllers.users import users
from app.api.controllers.users import messages
from fastapi.middleware.cors import CORSMiddleware
import os


import faiss
import numpy as np

DB_PATH = "/app/faiss/face_index.index"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    '''This function is used to test the connection to the service, It says hello world!'''
    return {"Hello": "World, Facial Recognition"}

if not os.path.exists(DB_PATH):
    # exemplo com índice L2, ajuste conforme necessário
    index = faiss.IndexFlatL2(128)  # ou a dimensão correta do seu vetor
    faiss.write_index(index, DB_PATH)

app.include_router(faces.router)
app.include_router(users.router)
app.include_router(messages.router)