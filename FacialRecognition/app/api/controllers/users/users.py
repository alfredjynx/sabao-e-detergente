from fastapi import File, Form, UploadFile, APIRouter
import os

router = APIRouter()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.post("/user/register")
async def register_user(
    username: str = Form(...),
    clerk_id: str = Form(...)
):
    """Registers a new user.
    Args:
        username (str): The name of the user.
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with "id" indicating uuid of person saved
    """
    response = await register_user_service(username, clerk_id)
    return response

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.get("/user/{clerk_id}")
async def get_user(
    clerk_id: str
):
    """Gets the user with the given clerk_id.
    Args:
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with the user data.
    """
    response = await get_user_service(clerk_id)
    return response