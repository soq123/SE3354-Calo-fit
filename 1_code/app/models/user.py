from flask_login import UserMixin
from app.db import get_db


class User(UserMixin):
    """Thin wrapper around a DB row that satisfies Flask-Login's interface."""

    def __init__(self, row):
        self.id = row["user_id"]
        self.username = row["username"]
        self.email = row["email"]
        self.password_hash = row["password_hash"]
        self.calorie_goal = row["calorie_goal"]
        self.email_verified = bool(row["email_verified"])

    def get_id(self):
        return str(self.id)


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    return User(row) if row else None


def get_user_by_username(username):
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)
    ).fetchone()
    return User(row) if row else None


def get_user_by_email(email):
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)
    ).fetchone()
    return User(row) if row else None


def create_user(username, email, password_hash, calorie_goal=2000):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, email, password_hash, calorie_goal) VALUES (?, ?, ?, ?)",
        (username, email.lower(), password_hash, calorie_goal),
    )
    db.commit()
    return cursor.lastrowid


def verify_user_email(user_id):
    db = get_db()
    db.execute(
        "UPDATE users SET email_verified = 1 WHERE user_id = ?", (user_id,)
    )
    db.commit()


def update_password(user_id, password_hash):
    db = get_db()
    db.execute(
        "UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, user_id)
    )
    db.commit()


def update_calorie_goal(user_id, calorie_goal):
    db = get_db()
    db.execute(
        "UPDATE users SET calorie_goal = ? WHERE user_id = ?", (calorie_goal, user_id)
    )
    db.commit()
