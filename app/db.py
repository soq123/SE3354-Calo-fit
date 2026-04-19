import os
import sqlite3
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calofit.db')


CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    calorie_goal INTEGER NOT NULL DEFAULT 2000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_MEAL_LOGS = """
CREATE TABLE IF NOT EXISTS meal_logs (
    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fats REAL DEFAULT 0,
    meal_type TEXT NOT NULL CHECK(meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')),
    log_date DATE NOT NULL,
    log_time TIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
"""

CREATE_MOOD_LOGS = """
CREATE TABLE IF NOT EXISTS mood_logs (
    mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    energy_level INTEGER NOT NULL CHECK(energy_level BETWEEN 1 AND 5),
    notes TEXT,
    log_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()



def init_db():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()



def ensure_schema_compatibility():
    db = get_db()
    db.execute(CREATE_USERS)
    db.execute(CREATE_MEAL_LOGS)
    db.execute(CREATE_MOOD_LOGS)
    db.commit()



def ensure_default_user():
    db = get_db()
    existing = db.execute("SELECT user_id FROM users WHERE email = ?", ("demo@calofit.com",)).fetchone()
    demo_hash = generate_password_hash('demo123')
    if not existing:
        db.execute(
            """INSERT INTO users (username, email, password_hash, calorie_goal)
               VALUES (?, ?, ?, ?)""",
            ('demo', 'demo@calofit.com', demo_hash, 2000),
        )
    else:
        db.execute(
            "UPDATE users SET username = ?, password_hash = ?, calorie_goal = ? WHERE email = ?",
            ('demo', demo_hash, 2000, 'demo@calofit.com'),
        )
    db.commit()



def init_app(app):
    app.teardown_appcontext(close_db)
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    with app.app_context():
        if not os.path.exists(DATABASE):
            init_db()
        ensure_schema_compatibility()
        ensure_default_user()
