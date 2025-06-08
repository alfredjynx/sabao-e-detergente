import mysql.connector
from uuid import uuid4
from datetime import datetime

# Conexão com o banco de dados

db = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="bubble"
)
cursor = db.cursor(dictionary=True)

def create_message_service(user_id: str, content: str):
    message_id = str(uuid4())
    cursor.execute(
        "INSERT INTO messages (id, user_id, content, created_at) VALUES (%s, %s, %s, %s)",
        (message_id, user_id, content, datetime.now())
    )
    db.commit()
    return {"id": message_id, "user_id": user_id, "content": content}

def get_feed_service(user_id: str):
    # Busca os usuários que o user_id segue
    cursor.execute("SELECT id_followed FROM user_follow WHERE id_follow = %s", (user_id,))
    followed = [row["id_followed"] for row in cursor.fetchall()]
    if not followed:
        return {"messages": []}
    # Busca as mensagens dos seguidos
    format_strings = ','.join(['%s'] * len(followed))
    cursor.execute(f"SELECT * FROM messages WHERE user_id IN ({format_strings}) ORDER BY created_at DESC", tuple(followed))
    messages = cursor.fetchall()
    return {"messages": messages}
