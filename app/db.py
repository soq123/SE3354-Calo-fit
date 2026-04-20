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
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('users', 'meal_logs', 'mood_logs')"
    ).fetchone()
    return result[0] == 3

def init_db():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())
    db.commit()

def _migrate(app):
    """Apply incremental schema changes that may not exist on older DBs."""
    from sqlite3 import OperationalError
    with app.app_context():
        db = get_db()
        try:
            db.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
            db.commit()
        except OperationalError:
            pass  # column already exists
        try:
            db.execute("""CREATE TABLE IF NOT EXISTS mood_logs (
                mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood TEXT NOT NULL,
                energy_level INTEGER NOT NULL CHECK(energy_level BETWEEN 1 AND 5),
                notes TEXT,
                log_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )""")
            db.commit()
        except OperationalError:
            pass  # table already exists

def init_app(app):
    app.teardown_appcontext(close_db)
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    with app.app_context():
        if not tables_exist():
            init_db()
    _migrate(app)
