from app.db import get_db


def add_mood_entry(user_id, mood, energy_level, note, log_date):
    db = get_db()
    db.execute(
        """INSERT INTO mood_logs (user_id, mood, energy_level, notes, log_date)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, mood, energy_level, note, log_date),
    )
    db.commit()


def get_latest_mood_for_date(user_id, log_date):
    db = get_db()
    row = db.execute(
        """SELECT mood_id, mood, energy_level, notes, log_date, created_at
           FROM mood_logs
           WHERE user_id = ? AND log_date = ?
           ORDER BY created_at DESC, mood_id DESC
           LIMIT 1""",
        (user_id, log_date),
    ).fetchone()
    return dict(row) if row else None


def get_recent_moods(user_id, limit=7):
    db = get_db()
    rows = db.execute(
        """SELECT mood_id, mood, energy_level, notes, log_date, created_at
           FROM mood_logs
           WHERE user_id = ?
           ORDER BY log_date DESC, created_at DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def get_weekly_mood_summary(user_id, start_date, end_date):
    db = get_db()
    rows = db.execute(
        """SELECT log_date,
                  COUNT(*) AS entry_count,
                  ROUND(AVG(energy_level), 1) AS avg_energy,
                  GROUP_CONCAT(mood, ', ') AS moods
           FROM mood_logs
           WHERE user_id = ? AND log_date BETWEEN ? AND ?
           GROUP BY log_date
           ORDER BY log_date""",
        (user_id, start_date, end_date),
    ).fetchall()
    return [dict(row) for row in rows]


def get_top_moods(user_id, start_date, end_date):
    db = get_db()
    rows = db.execute(
        """SELECT mood, COUNT(*) AS count
           FROM mood_logs
           WHERE user_id = ? AND log_date BETWEEN ? AND ?
           GROUP BY mood
           ORDER BY count DESC, mood ASC""",
        (user_id, start_date, end_date),
    ).fetchall()
    return [dict(row) for row in rows]
