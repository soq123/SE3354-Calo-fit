from app.db import get_db


def get_favorites(user_id):
    db = get_db()
    rows = db.execute(
        """SELECT fav_id, food_name, calories, protein, carbs, fats,
                  iron, zinc, calcium, meal_type
           FROM favorites
           WHERE user_id = ?
           ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def add_favorite(user_id, food_name, calories, protein=0, carbs=0,
                 fats=0, iron=0, zinc=0, calcium=0, meal_type=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO favorites
               (user_id, food_name, calories, protein, carbs, fats, iron, zinc, calcium, meal_type)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, food_name, calories, protein, carbs, fats, iron, zinc, calcium, meal_type)
    )
    db.commit()
    return cur.lastrowid


def delete_favorite(fav_id, user_id):
    db = get_db()
    db.execute(
        "DELETE FROM favorites WHERE fav_id = ? AND user_id = ?",
        (fav_id, user_id)
    )
    db.commit()


def get_favorite_by_id(fav_id, user_id):
    db = get_db()
    row = db.execute(
        """SELECT fav_id, food_name, calories, protein, carbs, fats,
                  iron, zinc, calcium, meal_type
           FROM favorites WHERE fav_id = ? AND user_id = ?""",
        (fav_id, user_id)
    ).fetchone()
    return dict(row) if row else None
