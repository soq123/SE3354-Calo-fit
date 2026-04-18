from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from app.models.meal import (
    add_meal, get_meals_by_date, get_daily_total,
    get_daily_macros, get_remaining_calories, delete_meal, update_meal
)
from app.models.food_entry import get_all_meals_for_user, get_meal_by_id

meals_bp = Blueprint("meals", __name__)

USER_ID = 1

@meals_bp.route("/")
def home():
    today = date.today().isoformat()
    meals = get_meals_by_date(USER_ID, today)
    total_calories = get_daily_total(USER_ID, today)
    macros = get_daily_macros(USER_ID, today)
    remaining_info = get_remaining_calories(USER_ID, today)
    calories_remaining = remaining_info["remaining"]
    calorie_goal = remaining_info["calorie_goal"]
    return render_template(
        "index.html",
        meals=meals,
        today=today,
        total_calories=total_calories,
        macros=macros,
        calories_remaining=calories_remaining,
        calorie_goal=calorie_goal
    )

@meals_bp.route("/meals/new", methods=["GET", "POST"])
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

        add_meal(USER_ID, food_name, int(calories), meal_type, log_date,
                 float(protein), float(carbs), float(fats))
        flash("Meal added successfully!", "success")
        return redirect(url_for("meals.home"))

    return render_template("add_meal.html", today=date.today().isoformat())

@meals_bp.route("/meals/history")
def meal_history():
    meals = get_all_meals_for_user(USER_ID)
    return render_template("meal_history.html", meals=meals)

@meals_bp.route("/meals/<int:meal_id>")
def meal_details(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal:
        flash("Meal not found.", "danger")
        return redirect(url_for("meals.meal_history"))
    return render_template("meal_info.html", meal=meal)

@meals_bp.route("/meals/<int:meal_id>/edit", methods=["GET", "POST"])
def edit_meal(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal:
        flash("Meal not found.", "danger")
        return redirect(url_for("meals.meal_history"))

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
            return render_template("edit_meal.html", meal=meal)

        update_meal(meal_id, USER_ID, food_name, int(calories),
                    float(protein), float(carbs), float(fats), meal_type, log_date)
        flash("Meal updated successfully!", "success")
        return redirect(url_for("meals.meal_details", meal_id=meal_id))

    return render_template("edit_meal.html", meal=meal)

@meals_bp.route("/meals/<int:meal_id>/delete", methods=["POST"])
def delete_meal_entry(meal_id):
    delete_meal(meal_id, USER_ID)
    flash("Meal deleted.", "info")
    return redirect(url_for("meals.meal_history"))
