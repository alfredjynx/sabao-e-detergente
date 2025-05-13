from fastapi import File, Form, UploadFile, APIRouter
import os
from app.api.service.users.users import *

router = APIRouter()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

@router.post("/users")
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

@router.get("/users/{clerk_id}")
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

@router.get("/users")
async def get_all_users():
    """Gets all users.
    Returns:
        dict: Returns a dictionary with all users.
    """
    response = await get_all_users_service()
    return response

@router.delete("/users/{clerk_id}")
async def delete_user(
    clerk_id: str
):
    """Deletes the user with the given clerk_id.
    Args:
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with the user data.
    """
    response = await delete_user_service(clerk_id)
    return response

@router.post("/users/follow")
async def follow_user(
    clerk_id: str = Form(...),
    clerk_id_followed: str = Form(...)
):
    response =  await user_follow_service(clerk_id=clerk_id, followed_clerk_id=clerk_id_followed)
    return response