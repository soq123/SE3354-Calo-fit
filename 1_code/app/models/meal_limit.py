from app.db import get_db

MEAL_TYPES = ('Breakfast', 'Lunch', 'Dinner', 'Snack')


def get_limits(user_id):
    db = get_db()
    rows = db.execute(
        "SELECT meal_type, calorie_limit FROM meal_type_limits WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    limits = {mt: 0 for mt in MEAL_TYPES}
    for row in rows:
        limits[row['meal_type']] = row['calorie_limit']
    return limits


def set_limit(user_id, meal_type, calorie_limit):
    if meal_type not in MEAL_TYPES:
        return
    db = get_db()
    db.execute(
        """INSERT INTO meal_type_limits (user_id, meal_type, calorie_limit)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id, meal_type)
           DO UPDATE SET calorie_limit = excluded.calorie_limit""",
        (user_id, meal_type, int(calorie_limit))
    )
    db.commit()


def get_meal_type_totals(user_id, log_date):
    db = get_db()
    rows = db.execute(
        """SELECT meal_type, COALESCE(SUM(calories), 0) AS total
           FROM meal_logs
           WHERE user_id = ? AND log_date = ?
           GROUP BY meal_type""",
        (user_id, log_date)
    ).fetchall()
    totals = {mt: 0 for mt in MEAL_TYPES}
    for row in rows:
        totals[row['meal_type']] = row['total']
    return totals
