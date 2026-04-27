PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS mood_logs;
DROP TABLE IF EXISTS meal_logs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    calorie_goal INTEGER NOT NULL DEFAULT 2000,
    email_verified INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meal_logs (
    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fats REAL DEFAULT 0,
    iron REAL DEFAULT 0,
    zinc REAL DEFAULT 0,
    calcium REAL DEFAULT 0,
    meal_type TEXT NOT NULL CHECK(meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')),
    log_date DATE NOT NULL,
    log_time TIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS meal_type_limits (
    limit_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(user_id),
    meal_type     TEXT    NOT NULL CHECK(meal_type IN ('Breakfast','Lunch','Dinner','Snack')),
    calorie_limit INTEGER NOT NULL DEFAULT 0,
    UNIQUE(user_id, meal_type)
);

CREATE TABLE IF NOT EXISTS favorites (
    fav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id),
    food_name   TEXT    NOT NULL,
    calories    REAL    NOT NULL DEFAULT 0,
    protein     REAL    NOT NULL DEFAULT 0,
    carbs       REAL    NOT NULL DEFAULT 0,
    fats        REAL    NOT NULL DEFAULT 0,
    iron        REAL    NOT NULL DEFAULT 0,
    zinc        REAL    NOT NULL DEFAULT 0,
    calcium     REAL    NOT NULL DEFAULT 0,
    meal_type   TEXT    DEFAULT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mood_logs (
    mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    energy_level INTEGER NOT NULL CHECK(energy_level BETWEEN 1 AND 5),
    notes TEXT,
    log_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
