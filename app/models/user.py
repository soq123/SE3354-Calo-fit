from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db


def create_user(username, email, password, calorie_goal=2000):
    db = get_db()
    password_hash = generate_password_hash(password)
    cursor = db.execute(
        """INSERT INTO users (username, email, password_hash, calorie_goal)
           VALUES (?, ?, ?, ?)""",
        (username, email, password_hash, calorie_goal),
    )
    db.commit()
    return cursor.lastrowid


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute(
        "SELECT user_id, username, email, password_hash, calorie_goal, created_at FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def get_user_by_email(email):
    db = get_db()
    row = db.execute(
        "SELECT user_id, username, email, password_hash, calorie_goal, created_at FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    return dict(row) if row else None


def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
