from fastapi import APIRouter, Form
from app.api.services.users.messages import create_message_service, get_feed_service

router = APIRouter()

@router.post("/messages")
async def post_message(
    user_id: str = Form(...),
    content: str = Form(...)
):
    return create_message_service(user_id, content)

@router.get("/feed/{user_id}")
async def get_feed(user_id: str):
    return get_feed_service(user_id)
