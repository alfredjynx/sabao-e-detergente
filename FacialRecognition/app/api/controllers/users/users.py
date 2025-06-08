from fastapi import File, Form, UploadFile, APIRouter
import os
from app.api.services.users.users import *

router = APIRouter()

@router.post("/users")
async def register_user(
    username: str = Form(...),
    clerk_id: str = Form(...)
):
    response = await register_user_service(username, clerk_id)
    return response

@router.get("/users/{clerk_id}")
async def get_user(
    clerk_id: str
):
    response = await get_user_service(clerk_id)
    return response

@router.get("/users")
async def get_all_users():
    response = await get_all_users_service()
    return response

@router.delete("/users/{clerk_id}")
async def delete_user(
    clerk_id: str
):
    response = await delete_user_service(clerk_id)
    return response

@router.post("/users/{followed_clerk_id}/follow")
async def follow_user(
    followed_clerk_id: str,
    clerk_id: str = Form(...)
):
    response =  await user_follow_service(clerk_id=clerk_id, followed_clerk_id=followed_clerk_id)
    return response

@router.delete("/users/{followed_clerk_id}/follow")
async def unfollow_user(
    followed_clerk_id: str,
    clerk_id: str = Form(...)
):
    response =  await user_unfollow_service(clerk_id=clerk_id, followed_clerk_id=followed_clerk_id)
    return response

@router.get("/users/{clerk_id}/followers")
async def get_followers(
    clerk_id: str
):
    response =  await get_followers_service(clerk_id=clerk_id)
    return response

@router.get("/users/{clerk_id}/following")
async def get_following(
    clerk_id: str
):
    response =  await get_following_service(clerk_id=clerk_id)
    return response

@router.post("/users/follow-by-photo/")
async def follow_by_photo(
    file: UploadFile = File(...),
    clerk_id: str = Form(...)
):
    response = await follow_by_photo_service(file, clerk_id)
    return response