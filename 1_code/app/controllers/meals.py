from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from app.models.meal import (
    add_meal, get_meals_by_date, get_daily_total,
    get_daily_macros, get_remaining_calories, delete_meal, update_meal, get_streak
)
from app.models.food_entry import get_all_meals_for_user, get_meal_by_id
from app.models.mood import get_latest_mood_for_date
from app.services.insights import generate_recommendations

TIPS = [
    "Try to include protein in every meal to stay full and build muscle!",
    "Drinking water before meals can help you avoid overeating.",
    "Colorful plates mean more nutrients — add a veggie today!",
    "Eating slowly helps your brain catch up with your stomach.",
    "A consistent meal schedule can improve your energy levels.",
    "Healthy snacks like nuts or fruit keep cravings at bay.",
    "Aim for at least 5 servings of fruits and vegetables daily.",
]

meals_bp = Blueprint("meals", __name__)


@meals_bp.route("/")
@login_required
def home():
    today = date.today().isoformat()
    meals = get_meals_by_date(current_user.id, today)
    total_calories = get_daily_total(current_user.id, today)
    macros = get_daily_macros(current_user.id, today)
    remaining_info = get_remaining_calories(current_user.id, today)
    calories_remaining = remaining_info["remaining"]
    calorie_goal = remaining_info["calorie_goal"]
    latest_mood = get_latest_mood_for_date(current_user.id, today)
    recommendations = generate_recommendations(
        macros, calorie_goal, remaining_info["consumed"], latest_mood
    )
    streak = get_streak(current_user.id)
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    meal_types_today = {m['meal_type'] for m in meals}
    missing_snack = len(meals) > 0 and 'Snack' not in meal_types_today
    return render_template(
        "index.html",
        meals=meals,
        today=today,
        total_calories=total_calories,
        macros=macros,
        calories_remaining=calories_remaining,
        calorie_goal=calorie_goal,
        latest_mood=latest_mood,
        recommendations=recommendations,
        streak=streak,
        greeting=greeting,
        tip=tip,
        missing_snack=missing_snack,
    )


@meals_bp.route("/meals/new", methods=["GET", "POST"])
@login_required
def new_meal():
    if request.method == "POST":
        food_name = request.form.get("food_name", "").strip()
        meal_type = request.form.get("meal_type", "").strip()
        log_date = request.form.get("log_date", "").strip()
        calories = request.form.get("calories", 0)
        protein = request.form.get("protein", 0)
        carbs = request.form.get("carbs", 0)
        fats = request.form.get("fats", 0)

        if not food_name or not meal_type or not log_date or not calories:
            flash("Please fill in all required fields.", "danger")
            return render_template("add_meal.html")

        add_meal(current_user.id, food_name, int(calories), meal_type, log_date,
                 float(protein), float(carbs), float(fats))
        flash("Meal added successfully!", "success")
        return redirect(url_for("meals.home"))

    return render_template("add_meal.html", today=date.today().isoformat())


@meals_bp.route("/meals/history")
@login_required
def meal_history():
    meals = get_all_meals_for_user(current_user.id)
    return render_template("meal_history.html", meals=meals)


@meals_bp.route("/meals/<int:meal_id>")
@login_required
def meal_details(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal or meal["user_id"] != current_user.id:
        flash("Meal not found.", "danger")
        return redirect(url_for("meals.meal_history"))
    return render_template("meal_info.html", meal=meal)


@meals_bp.route("/meals/<int:meal_id>/edit", methods=["GET", "PATCH"])
@login_required
def edit_meal(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal or meal["user_id"] != current_user.id:
        if request.method == "PATCH":
            return jsonify({"status": "error", "message": "Meal not found."}), 404
        flash("Meal not found.", "danger")
        return redirect(url_for("meals.meal_history"))

    if request.method == "PATCH":
        data = request.get_json(silent=True) or {}
        food_name = data.get("food_name", "").strip()
        meal_type = data.get("meal_type", "").strip()
        log_date = data.get("log_date", "").strip()
        calories = data.get("calories", 0)
        protein = data.get("protein", 0)
        carbs = data.get("carbs", 0)
        fats = data.get("fats", 0)

        if not food_name or not meal_type or not log_date or not calories:
            return jsonify({"status": "error", "message": "Please fill in all required fields."}), 400

        update_meal(meal_id, current_user.id, food_name, int(calories),
                    float(protein or 0), float(carbs or 0), float(fats or 0), meal_type, log_date)
        return jsonify({"status": "ok", "redirect": url_for("meals.meal_details", meal_id=meal_id)})

    return render_template("edit_meal.html", meal=meal)


@meals_bp.route("/meals/<int:meal_id>/delete", methods=["DELETE"])
@login_required
def delete_meal_entry(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal or meal["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Meal not found."}), 404
    delete_meal(meal_id, current_user.id)
    return jsonify({"status": "ok", "redirect": url_for("meals.meal_history")})
