import sqlite3
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
TEST_DB = os.path.join(os.path.dirname(__file__), 'test_calofit.db')
SCHEMA_PATH = os.path.join(ROOT, 'schema.sql')

passed = 0
failed = 0
passed = 0
failed = 0

def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.execute(
        "INSERT INTO users (username, email, password_hash, calorie_goal) VALUES (?, ?, ?, ?)",
        ('testuser', 'test@test.com', 'pw', 2000)
    )
    test_meals = [
        (1, 'Oatmeal', 300, 10, 50, 5, 'Breakfast', '2026-04-10'),
        (1, 'Chicken Rice', 650, 45, 60, 18, 'Lunch', '2026-04-10'),
        (1, 'Salmon Dinner', 700, 40, 35, 30, 'Dinner', '2026-04-10'),
        (1, 'Protein Bar', 200, 20, 25, 8, 'Snack', '2026-04-10'),
        (1, 'Eggs', 400, 22, 5, 28, 'Breakfast', '2026-04-11'),
        (1, 'Turkey Wrap', 500, 32, 40, 14, 'Lunch', '2026-04-11'),
        (1, 'Pasta', 800, 25, 95, 22, 'Dinner', '2026-04-11'),
        (1, 'Toast', 350, 8, 40, 12, 'Breakfast', '2026-04-12'),
        (1, 'Salad', 450, 30, 20, 18, 'Lunch', '2026-04-12'),
    ]
    conn.executemany(
        """INSERT INTO meal_logs
           (user_id, food_name, calories, protein, carbs, fats, meal_type, log_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        test_meals
    )
    conn.commit()
    return conn

def run_test(test_name, actual, expected):
    global passed, failed
    if actual == expected:
        print(f"  PASS: {test_name}")
        print(f"         Expected: {expected}, Got: {actual}")
        passed += 1
    else:
        print(f"  FAIL: {test_name}")
        print(f"         Expected: {expected}, Got: {actual}")
        failed += 1

def test_daily_total(conn):
    print("\nTest 1: Daily Calorie Total")
    result = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-10'"
    ).fetchone()
    run_test("April 10 total (300+650+700+200)", result['total'], 1850)
    result = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-11'"
    ).fetchone()
    run_test("April 11 total (400+500+800)", result['total'], 1700)
    result = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-12'"
    ).fetchone()
    run_test("April 12 total (350+450)", result['total'], 800)

def test_remaining_calories(conn):
    print("\nTest 2: Remaining Calories vs Goal")
    result = conn.execute(
        """SELECT u.calorie_goal - COALESCE(SUM(m.calories), 0) AS remaining
           FROM users u
           LEFT JOIN meal_logs m ON u.user_id = m.user_id AND m.log_date = '2026-04-10'
           WHERE u.user_id = 1""",
    ).fetchone()
    run_test("April 10 remaining (2000-1850)", result['remaining'], 150)
    result = conn.execute(
        """SELECT u.calorie_goal - COALESCE(SUM(m.calories), 0) AS remaining
           FROM users u
           LEFT JOIN meal_logs m ON u.user_id = m.user_id AND m.log_date = '2026-04-11'
           WHERE u.user_id = 1""",
    ).fetchone()
    run_test("April 11 remaining (2000-1700)", result['remaining'], 300)

def test_weekly_summary(conn):
    print("\nTest 3: Weekly Summary")
    rows = conn.execute(
        """SELECT log_date, SUM(calories) AS total
           FROM meal_logs
           WHERE user_id = 1 AND log_date BETWEEN '2026-04-10' AND '2026-04-12'
           GROUP BY log_date
           ORDER BY log_date"""
    ).fetchall()
    run_test("Number of days with data", len(rows), 3)
    run_test("Day 1 total", rows[0]['total'], 1850)
    run_test("Day 2 total", rows[1]['total'], 1700)
    run_test("Day 3 total", rows[2]['total'], 800)

def test_weekly_average(conn):
    print("\nTest 4: Weekly Average")
    result = conn.execute(
        """SELECT AVG(daily_total) AS avg_cal
           FROM (
               SELECT SUM(calories) AS daily_total
               FROM meal_logs
               WHERE user_id = 1 AND log_date BETWEEN '2026-04-10' AND '2026-04-12'
               GROUP BY log_date
           )"""
    ).fetchone()
    run_test("Average daily calories", round(result['avg_cal'], 1), 1450.0)

def test_meal_count(conn):
    print("\nTest 5: Meal Count Per Day")
    result = conn.execute(
        "SELECT COUNT(*) AS cnt FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-10'"
    ).fetchone()
    run_test("April 10 meal count", result['cnt'], 4)
    result = conn.execute(
        "SELECT COUNT(*) AS cnt FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-11'"
    ).fetchone()
    run_test("April 11 meal count", result['cnt'], 3)

def test_meal_insertion(conn):
    print("\nTest 6: Meal Insertion")
    before = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-12'"
    ).fetchone()['total']
    conn.execute(
        """INSERT INTO meal_logs (user_id, food_name, calories, protein, carbs, fats, meal_type, log_date)
           VALUES (1, 'Test Snack', 250, 10, 20, 8, 'Snack', '2026-04-12')"""
    )
    conn.commit()
    after = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-12'"
    ).fetchone()['total']
    run_test("Total increased by 250", after - before, 250)
    run_test("New total is correct (800+250)", after, 1050)

def test_meal_deletion(conn):
    print("\nTest 7: Meal Deletion")
    meal = conn.execute(
        "SELECT meal_id FROM meal_logs WHERE food_name = 'Test Snack'"
    ).fetchone()
    conn.execute("DELETE FROM meal_logs WHERE meal_id = ?", (meal['meal_id'],))
    conn.commit()
    after = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-04-12'"
    ).fetchone()['total']
    run_test("Total after deletion back to 800", after, 800)

def test_empty_day(conn):
    print("\nTest 8: Empty Day Returns Zero")
    result = conn.execute(
        "SELECT COALESCE(SUM(calories), 0) AS total FROM meal_logs WHERE user_id = 1 AND log_date = '2026-01-01'"
    ).fetchone()
    run_test("Day with no meals = 0", result['total'], 0)

if __name__ == "__main__":
    print("=" * 55)
    print("CaloFit - Basic Function Tests")
    print("=" * 55)
    conn = setup_test_db()
    test_daily_total(conn)
    test_remaining_calories(conn)
    test_weekly_summary(conn)
    test_weekly_average(conn)
    test_meal_count(conn)
    test_meal_insertion(conn)
    test_meal_deletion(conn)
    test_empty_day(conn)
    conn.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    print("\n" + "=" * 55)
    print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 55)
    if failed > 0:
        sys.exit(1)
