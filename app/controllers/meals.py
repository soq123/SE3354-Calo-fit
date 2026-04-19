from datetime import date
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.models.food_entry import get_all_meals_for_user, get_meal_by_id
from app.models.meal import (
    add_meal,
    delete_meal,
    get_daily_macros,
    get_daily_total,
    get_meals_by_date,
    get_remaining_calories,
    update_meal,
)
from app.models.mood import get_latest_mood_for_date
from app.services.insights import generate_recommendations

meals_bp = Blueprint("meals", __name__)



def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not g.get("user"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


@meals_bp.route("/")
@login_required
def home():
    today = date.today().isoformat()
    user_id = g.user["user_id"]
    meals = get_meals_by_date(user_id, today)
    total_calories = get_daily_total(user_id, today)
    macros = get_daily_macros(user_id, today)
    remaining_info = get_remaining_calories(user_id, today)
    latest_mood = get_latest_mood_for_date(user_id, today)
    recommendations = generate_recommendations(
        macros,
        remaining_info["calorie_goal"],
        remaining_info["consumed"],
        latest_mood,
    )
    reminder_message = None
    if not meals:
        reminder_message = "You have not logged any meals today yet. Add your first meal to stay on track."
    elif remaining_info["remaining"] > 0:
        reminder_message = f"You still have {remaining_info['remaining']} calories remaining today."

    return render_template(
        "index.html",
        meals=meals,
        today=today,
        total_calories=total_calories,
        macros=macros,
        calories_remaining=remaining_info["remaining"],
        calorie_goal=remaining_info["calorie_goal"],
        latest_mood=latest_mood,
        recommendations=recommendations,
        reminder_message=reminder_message,
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
            return render_template("add_meal.html", today=date.today().isoformat(), form=request.form)

        add_meal(
            g.user["user_id"],
            food_name,
            int(float(calories)),
            meal_type,
            log_date,
            float(protein or 0),
            float(carbs or 0),
            float(fats or 0),
        )
        flash("Meal added successfully!", "success")
        return redirect(url_for("meals.home"))

    return render_template("add_meal.html", today=date.today().isoformat(), form={})


@meals_bp.route("/meals/history")
@login_required
def meal_history():
    meals = get_all_meals_for_user(g.user["user_id"])
    return render_template("meal_history.html", meals=meals)


@meals_bp.route("/meals/<int:meal_id>")
@login_required
def meal_details(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal or meal["user_id"] != g.user["user_id"]:
        flash("Meal not found.", "danger")
        return redirect(url_for("meals.meal_history"))
    return render_template("meal_info.html", meal=meal)


@meals_bp.route("/meals/<int:meal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meal(meal_id):
    meal = get_meal_by_id(meal_id)
    if not meal or meal["user_id"] != g.user["user_id"]:
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

        update_meal(
            meal_id,
            g.user["user_id"],
            food_name,
            int(float(calories)),
            float(protein or 0),
            float(carbs or 0),
            float(fats or 0),
            meal_type,
            log_date,
        )
        flash("Meal updated successfully!", "success")
        return redirect(url_for("meals.meal_details", meal_id=meal_id))

    return render_template("edit_meal.html", meal=meal)


@meals_bp.route("/meals/<int:meal_id>/delete", methods=["POST"])
@login_required
def delete_meal_entry(meal_id):
    delete_meal(meal_id, g.user["user_id"])
    flash("Meal deleted.", "info")
    return redirect(url_for("meals.meal_history"))
