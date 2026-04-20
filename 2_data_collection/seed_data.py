import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'calofit.db')
SCHEMA_PATH = os.path.join(ROOT, 'schema.sql')

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())

    users = [
        ('yash', 'yash@example.com', 'hashed_pw_1', 2200),
        ('sohaib', 'sohaib@example.com', 'hashed_pw_2', 2500),
        ('dominic', 'dominic@example.com', 'hashed_pw_3', 2000),
        ('oliver', 'oliver@example.com', 'hashed_pw_4', 1800),
    ]
    cursor.executemany(
        "INSERT INTO users (username, email, password_hash, calorie_goal) VALUES (?, ?, ?, ?)",
        users
    )

    meals = [
        (1, 'Oatmeal with Banana', 350, 10, 55, 8, 'Breakfast', '2026-04-06'),
        (1, 'Grilled Chicken Salad', 420, 35, 20, 12, 'Lunch', '2026-04-06'),
        (1, 'Protein Bar', 250, 20, 25, 9, 'Snack', '2026-04-06'),
        (1, 'Salmon with Rice', 850, 45, 70, 28, 'Dinner', '2026-04-06'),
        (1, 'Scrambled Eggs and Toast', 400, 22, 30, 18, 'Breakfast', '2026-04-07'),
        (1, 'Turkey Wrap', 500, 32, 40, 14, 'Lunch', '2026-04-07'),
        (1, 'Greek Yogurt', 150, 15, 12, 4, 'Snack', '2026-04-07'),
        (1, 'Steak and Potatoes', 750, 50, 45, 30, 'Dinner', '2026-04-07'),
        (1, 'Protein Shake', 350, 40, 20, 5, 'Snack', '2026-04-07'),
        (1, 'Pancakes with Syrup', 550, 10, 80, 15, 'Breakfast', '2026-04-08'),
        (1, 'Chicken Rice Bowl', 650, 45, 60, 18, 'Lunch', '2026-04-08'),
        (1, 'Apple and Peanut Butter', 300, 8, 30, 16, 'Snack', '2026-04-08'),
        (1, 'Pasta with Meat Sauce', 800, 35, 90, 25, 'Dinner', '2026-04-08'),
        (1, 'Smoothie Bowl', 400, 15, 55, 10, 'Breakfast', '2026-04-09'),
        (1, 'Tuna Sandwich', 450, 30, 35, 15, 'Lunch', '2026-04-09'),
        (1, 'Mixed Nuts', 200, 6, 8, 18, 'Snack', '2026-04-09'),
        (1, 'Chicken Stir Fry', 600, 40, 50, 15, 'Dinner', '2026-04-09'),
        (1, 'Cottage Cheese', 300, 28, 10, 12, 'Snack', '2026-04-09'),
        (1, 'Egg Sandwich', 400, 20, 30, 15, 'Breakfast', '2026-04-10'),
        (1, 'Burrito Bowl', 700, 38, 65, 22, 'Lunch', '2026-04-10'),
        (1, 'Banana', 100, 1, 27, 0, 'Snack', '2026-04-10'),
        (1, 'Grilled Fish and Veggies', 550, 42, 25, 18, 'Dinner', '2026-04-10'),
        (1, 'Protein Shake', 300, 35, 15, 5, 'Snack', '2026-04-10'),
        (1, 'French Toast', 500, 12, 60, 18, 'Breakfast', '2026-04-11'),
        (1, 'Cheeseburger and Fries', 950, 35, 80, 45, 'Lunch', '2026-04-11'),
        (1, 'Ice Cream', 350, 5, 40, 18, 'Snack', '2026-04-11'),
        (1, 'Pizza (3 slices)', 650, 25, 75, 25, 'Dinner', '2026-04-11'),
        (1, 'Avocado Toast', 350, 10, 30, 20, 'Breakfast', '2026-04-12'),
        (1, 'Chicken Caesar Salad', 450, 35, 15, 20, 'Lunch', '2026-04-12'),
        (1, 'Protein Bar', 300, 25, 28, 10, 'Snack', '2026-04-12'),
        (2, 'Cereal with Milk', 300, 8, 45, 6, 'Breakfast', '2026-04-10'),
        (2, 'Shawarma Plate', 750, 40, 60, 25, 'Lunch', '2026-04-10'),
        (2, 'Chicken Tikka', 600, 45, 20, 22, 'Dinner', '2026-04-10'),
        (2, 'Bagel with Cream Cheese', 350, 10, 50, 12, 'Breakfast', '2026-04-11'),
        (2, 'Lamb Gyro', 650, 30, 45, 28, 'Lunch', '2026-04-11'),
        (2, 'Biryani', 800, 35, 90, 25, 'Dinner', '2026-04-11'),
        (2, 'Eggs and Sausage', 450, 28, 5, 30, 'Breakfast', '2026-04-12'),
        (2, 'Grilled Chicken Wrap', 500, 35, 40, 15, 'Lunch', '2026-04-12'),
    ]
    cursor.executemany(
        """INSERT INTO meal_logs
           (user_id, food_name, calories, protein, carbs, fats, meal_type, log_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        meals
    )

    conn.commit()
    conn.close()
    print("Database seeded successfully!")
    print(f"  - {len(users)} users created")
    print(f"  - {len(meals)} meal entries inserted")

if __name__ == "__main__":
    seed()
