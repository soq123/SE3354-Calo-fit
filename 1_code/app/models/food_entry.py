from app.db import get_db


def get_all_meals_for_user(user_id):
    db = get_db()
    rows = db.execute(
        """SELECT meal_id, food_name, calories, protein, carbs, fats,
                  meal_type, log_date, log_time
           FROM meal_logs
           WHERE user_id = ?
           ORDER BY log_date DESC, log_time DESC""",
        (user_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def get_meal_by_id(meal_id):
    db = get_db()
    result = db.execute(
        """SELECT meal_id, user_id, food_name, calories, protein, carbs, fats,
                  meal_type, log_date, log_time
           FROM meal_logs
           WHERE meal_id = ?""",
        (meal_id,)
    ).fetchone()
    return dict(result) if result else None


def get_meals_by_type(user_id, meal_type, log_date):
    db = get_db()
    rows = db.execute(
        """SELECT meal_id, food_name, calories, protein, carbs, fats, log_time
           FROM meal_logs
           WHERE user_id = ? AND meal_type = ? AND log_date = ?
           ORDER BY log_time""",
        (user_id, meal_type, log_date)
    ).fetchall()
    return [dict(row) for row in rows]


def search_food_history(user_id, search_term):
    db = get_db()
    rows = db.execute(
        """SELECT DISTINCT food_name, calories, protein, carbs, fats
           FROM meal_logs
           WHERE user_id = ? AND food_name LIKE ?
           ORDER BY food_name""",
        (user_id, f'%{search_term}%')
    ).fetchall()
    return [dict(row) for row in rows]
