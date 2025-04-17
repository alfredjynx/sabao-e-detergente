from fastapi import FastAPI
from app.api import facialRecognition
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(facialRecognition.router)