import os
import base64
import numpy as np
import mysql.connector
import os
from uuid import uuid4
from app.api.services.faces.faces import delete_face_service
from app.api.services.db import db, cursor

async def get_user_service(clerk_id):
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()

    cursor.execute("SELECT * FROM face_embeddings WHERE clerk_id = %s", (clerk_id,))
    face_embeddings = cursor.fetchall() 
    has_face_embeddings = True if face_embeddings else False
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "clerk_id": result[2],
            "face_embeddings": has_face_embeddings
        }
    
    return {"error": "User not found"}
    
async def register_user_service(username, clerk_id):
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if result:
        return {"error": "User already exists"}

    user_id = str(uuid4())

    cursor.execute("INSERT INTO users (id, name, clerk_id) VALUES (%s, %s, %s)", (user_id, username, clerk_id))
    db.commit()
    
    return {"id": user_id, "clerk_id": clerk_id}

async def get_all_users_service():
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    
    users = []
    for row in result:
        users.append({
            "id": row[0],
            "username": row[1],
            "clerk_id": row[2]
        })
    
    return {"users": users}

async def delete_user_service(clerk_id):
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if not result:
        return {"error": "User not found"}
    
    cursor.execute("DELETE FROM users WHERE clerk_id = %s", (clerk_id,))
    db.commit()

    delete_face_service(clerk_id=clerk_id)
    
    return {
        "id": result[0],
        "username": result[1],
        "clerk_id": result[2]
    }

async def user_follow_service(clerk_id, followed_clerk_id):
    followed = await get_user_service(clerk_id=followed_clerk_id)
    following = await get_user_service(clerk_id=clerk_id)
    follow_id = str(uuid4())
    cursor.execute("INSERT INTO user_follow (id, id_follow, id_followed) VALUES (%s, %s, %s)", (follow_id, following["id"], followed["id"]))
    db.commit()
    return {
        "message": f"Succesfully Followed {followed['username']}"
    }

async def user_unfollow_service(clerk_id, followed_clerk_id):
    followed = await get_user_service(clerk_id=followed_clerk_id)
    following = await get_user_service(clerk_id=clerk_id)
    cursor.execute("DELETE FROM user_follow WHERE id_follow = %s AND id_followed = %s", (following["id"], followed["id"]))
    db.commit()
    return {
        "message": f"Succesfully Unfollowed {followed['username']}"
    }

async def get_followers_service(clerk_id):
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if not result:
        return {"error": "User not found"}

    cursor.execute("SELECT * FROM user_follow WHERE id_followed = %s", (result[0],))
    result = cursor.fetchall()
    
    followers = []
    for row in result:
        cursor.execute("SELECT * FROM users WHERE id = %s", (row[1],))
        follower = cursor.fetchone()
        if follower:
            followers.append({
                "id": follower[0],
                "username": follower[1],
                "clerk_id": follower[2]
            })
    print(followers)
    return {"followers": followers}

async def get_following_service(clerk_id):
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if not result:
        return {"error": "User not found"}
    print(result)
    cursor.execute("SELECT * FROM user_follow WHERE id_follow = %s", (result[0],))
    result = cursor.fetchall()
    print(result)
    following = []
    for row in result:
        print(row)
        cursor.execute("SELECT * FROM users WHERE id = %s", (row[2],))
        followed_user = cursor.fetchone()
        following.append({
            "id": followed_user[0],
            "username": followed_user[1],
            "clerk_id": followed_user[2]
        })
    print(following)
    return {"following": following}

async def follow_by_photo_service(file, clerk_id):
    from app.api.services.faces.faces import identify_face
    response = await identify_face(file)
    clerk_ids = response.get("clerk_ids", [])
    followed = []
    for followed_clerk_id in clerk_ids:
        if followed_clerk_id != clerk_id:
            await user_follow_service(clerk_id=clerk_id, followed_clerk_id=followed_clerk_id)
            followed.append(followed_clerk_id)
    return {"followed": followed}
