from app.db import get_db


def add_meal(user_id, food_name, calories, meal_type, log_date,
             protein=0, carbs=0, fats=0, iron=0, zinc=0, calcium=0):
    db = get_db()
    db.execute(
        """INSERT INTO meal_logs
           (user_id, food_name, calories, protein, carbs, fats, iron, zinc, calcium, meal_type, log_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, food_name, calories, protein, carbs, fats, iron, zinc, calcium, meal_type, log_date)
    )
    db.commit()


def get_meals_by_date(user_id, log_date):
    db = get_db()
    return db.execute(
        """SELECT meal_id, food_name, calories, protein, carbs, fats,
                  iron, zinc, calcium, meal_type, log_time
           FROM meal_logs
           WHERE user_id = ? AND log_date = ?
           ORDER BY log_time""",
        (user_id, log_date)
    ).fetchall()


def get_daily_total(user_id, log_date):
    db = get_db()
    result = db.execute(
        """SELECT COALESCE(SUM(calories), 0) AS total_calories
           FROM meal_logs
           WHERE user_id = ? AND log_date = ?""",
        (user_id, log_date)
    ).fetchone()
    return result['total_calories']


def get_daily_macros(user_id, log_date):
    db = get_db()
    result = db.execute(
        """SELECT
               COALESCE(SUM(protein), 0)  AS total_protein,
               COALESCE(SUM(carbs), 0)    AS total_carbs,
               COALESCE(SUM(fats), 0)     AS total_fats,
               COALESCE(SUM(iron), 0)     AS total_iron,
               COALESCE(SUM(zinc), 0)     AS total_zinc,
               COALESCE(SUM(calcium), 0)  AS total_calcium
           FROM meal_logs
           WHERE user_id = ? AND log_date = ?""",
        (user_id, log_date)
    ).fetchone()
    return dict(result)


def get_remaining_calories(user_id, log_date):
    db = get_db()
    result = db.execute(
        """SELECT
               u.calorie_goal,
               COALESCE(SUM(m.calories), 0) AS consumed,
               u.calorie_goal - COALESCE(SUM(m.calories), 0) AS remaining
           FROM users u
           LEFT JOIN meal_logs m
               ON u.user_id = m.user_id AND m.log_date = ?
           WHERE u.user_id = ?
           GROUP BY u.user_id""",
        (log_date, user_id)
    ).fetchone()
    return dict(result) if result else {'calorie_goal': 0, 'consumed': 0, 'remaining': 0}


def get_weekly_summary(user_id, start_date, end_date):
    db = get_db()
    rows = db.execute(
        """SELECT
               log_date,
               SUM(calories) AS total_calories,
               COUNT(*) AS meal_count
           FROM meal_logs
           WHERE user_id = ? AND log_date BETWEEN ? AND ?
           GROUP BY log_date
           ORDER BY log_date""",
        (user_id, start_date, end_date)
    ).fetchall()
    return [dict(row) for row in rows]


def get_weekly_average(user_id, start_date, end_date):
    db = get_db()
    result = db.execute(
        """SELECT
               COALESCE(AVG(daily_total), 0) AS avg_calories
           FROM (
               SELECT SUM(calories) AS daily_total
               FROM meal_logs
               WHERE user_id = ? AND log_date BETWEEN ? AND ?
               GROUP BY log_date
           )""",
        (user_id, start_date, end_date)
    ).fetchone()
    return round(result['avg_calories'], 1)


def delete_meal(meal_id, user_id):
    db = get_db()
    db.execute(
        "DELETE FROM meal_logs WHERE meal_id = ? AND user_id = ?",
        (meal_id, user_id)
    )
    db.commit()


def update_meal(meal_id, user_id, food_name, calories, protein, carbs, fats,
                meal_type, log_date, iron=0, zinc=0, calcium=0):
    db = get_db()
    db.execute(
        """UPDATE meal_logs
           SET food_name = ?, calories = ?, protein = ?, carbs = ?, fats = ?,
               iron = ?, zinc = ?, calcium = ?, meal_type = ?, log_date = ?
           WHERE meal_id = ? AND user_id = ?""",
        (food_name, calories, protein, carbs, fats,
         iron, zinc, calcium, meal_type, log_date, meal_id, user_id)
    )
    db.commit()


def get_streak(user_id):
    from datetime import date, timedelta
    db = get_db()
    rows = db.execute(
        """SELECT DISTINCT log_date FROM meal_logs
           WHERE user_id = ?
           ORDER BY log_date DESC""",
        (user_id,)
    ).fetchall()
    if not rows:
        return 0
    dates = [row['log_date'] for row in rows]
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if dates[0] not in (today, yesterday):
        return 0
    streak = 0
    check_date = date.fromisoformat(dates[0])
    for d in dates:
        if date.fromisoformat(d) == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak
