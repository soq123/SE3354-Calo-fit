import sqlite3
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calofit.db')

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

def tables_exist():
    db = get_db()
    result = db.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('users', 'meal_logs')"
    ).fetchone()
    return result[0] == 2

def init_db():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())
    db.commit()

def ensure_default_user():
    db = get_db()
    existing = db.execute("SELECT user_id FROM users WHERE user_id = 1").fetchone()
    if not existing:
        db.execute(
            """INSERT INTO users (user_id, username, email, password_hash, calorie_goal)
               VALUES (1, 'demo', 'demo@calofit.com', 'not_a_real_hash', 2000)"""
        )
        db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    with app.app_context():
        if not tables_exist():
            init_db()
        ensure_default_user()
