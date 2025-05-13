import os
import base64
import numpy as np
import mysql.connector
import os
from uuid import uuid4
from app.api.service.faces.deleteFace import delete_face_service

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor()

async def get_user_service(clerk_id):
    """Gets the user with the given clerk_id.
    Args:
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with the user data.
    """
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()

    #check if user has face embeddings in the database
    cursor.execute("SELECT * FROM face_embeddings WHERE clerk_id = %s", (clerk_id,))
    face_embeddings = cursor.fetchall() 
    #create a bool to check if the user has face embeddings in the database
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
    """Registers a new user in the database.
    Args:
        username (str): The name of the user.
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with "id" indicating uuid of person saved
    """
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if result:
        return {"error": "User already exists"}
    
    # Generate a new UUID for the user
    user_id = str(uuid4())
    
    # Insert the new user into the database
    cursor.execute("INSERT INTO users (id, name, clerk_id) VALUES (%s, %s, %s)", (user_id, username, clerk_id))
    db.commit()
    
    return {"id": user_id, "clerk_id": clerk_id}

async def get_all_users_service():
    """Gets all users from the database.
    Returns:
        dict: Returns a dictionary with all users.
    """
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
    """Deletes the user with the given clerk_id.
    Args:
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with the user data.
    """
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if not result:
        return {"error": "User not found"}
    
    # Delete the user from the database
    cursor.execute("DELETE FROM users WHERE clerk_id = %s", (clerk_id,))
    db.commit()

    #TODO: Delete the user's face embeddings from the database faiss index
    # # Assuming you have a function to delete the face embeddings from the faiss index
    delete_face_service(clerk_id=clerk_id)
    
    return {
        "id": result[0],
        "username": result[1],
        "clerk_id": result[2]
    }
    

async def user_follow_service(clerk_id, followed_clerk_id):
    

    followed = get_user_service(clerk_id=followed_clerk_id)
    
    following = get_user_service(clerk_id=clerk_id)
    
    
    
    # Insert the new user into the database
    cursor.execute("INSERT INTO user_follow (id_follow, id_followed) VALUES (%s, %s)", (following["id"], followed["id"]))
    db.commit()
    
    return {
        "message": f"Succesfully Followed {followed["username"]}"
    }
    