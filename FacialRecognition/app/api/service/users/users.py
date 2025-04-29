import os
import base64
import numpy as np
import mysql.connector
import os
from uuid import uuid4

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor()

def get_user_service(clerk_id):
    """Gets the user with the given clerk_id.
    Args:
        clerk_id (str): The email of the user.
    Returns:
        dict: Returns a dictionary with the user data.
    """
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
    result = cursor.fetchone()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "clerk_id": result[2]
        }
    
    return {"error": "User not found"}
    
def register_user_service(username, clerk_id):
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
    cursor.execute("INSERT INTO users (id, username, clerk_id) VALUES (%s, %s, %s)", (user_id, username, clerk_id))
    db.commit()
    
    return {"id": user_id}