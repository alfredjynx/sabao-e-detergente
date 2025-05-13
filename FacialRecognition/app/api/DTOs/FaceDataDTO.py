from pydantic import BaseModel

# --------------------------------------- #

class FaceData(BaseModel):
    name: str
    image: str
