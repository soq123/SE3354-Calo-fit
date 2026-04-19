from datetime import date, timedelta

from flask import Blueprint, g, jsonify, render_template

from app.controllers.meals import login_required
from app.models.meal import (
    get_daily_macros,
    get_daily_total,
    get_remaining_calories,
    get_weekly_average,
    get_weekly_summary,
)
from app.models.mood import get_top_moods, get_weekly_mood_summary
from app.services.insights import generate_recommendations, summarize_weekly_moods

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/daily/<int:user_id>")
@login_required
def daily_summary(user_id):
    today = date.today().isoformat()
    total = get_daily_total(user_id, today)
    macros = get_daily_macros(user_id, today)
    remaining = get_remaining_calories(user_id, today)
    return jsonify(
        {
            "user_id": user_id,
            "date": today,
            "total_calories": total,
            "macros": macros,
            "calorie_goal": remaining["calorie_goal"],
            "calories_remaining": remaining["remaining"],
        }
    )


@analytics_bp.route("/analytics/daily/<int:user_id>/<log_date>")
@login_required
def daily_summary_by_date(user_id, log_date):
    total = get_daily_total(user_id, log_date)
    macros = get_daily_macros(user_id, log_date)
    remaining = get_remaining_calories(user_id, log_date)
    return jsonify(
        {
            "user_id": user_id,
            "date": log_date,
            "total_calories": total,
            "macros": macros,
            "calorie_goal": remaining["calorie_goal"],
            "calories_remaining": remaining["remaining"],
        }
    )


@analytics_bp.route("/analytics/weekly")
@login_required
def weekly_summary():
    today = date.today()
    week_ago = today - timedelta(days=6)
    user_id = g.user["user_id"]
    summary = get_weekly_summary(user_id, week_ago.isoformat(), today.isoformat())
    average = get_weekly_average(user_id, week_ago.isoformat(), today.isoformat())
    remaining_today = get_remaining_calories(user_id, today.isoformat())
    mood_summary_rows = get_weekly_mood_summary(user_id, week_ago.isoformat(), today.isoformat())
    top_moods = get_top_moods(user_id, week_ago.isoformat(), today.isoformat())
    mood_overview = summarize_weekly_moods(mood_summary_rows, top_moods)
    total_meals = sum(day["meal_count"] for day in summary)
    macro_totals = {
        "protein": 0,
        "carbs": 0,
        "fats": 0,
    }
    for day in summary:
        day_macros = get_daily_macros(user_id, day["log_date"])
        macro_totals["protein"] += float(day_macros["total_protein"])
        macro_totals["carbs"] += float(day_macros["total_carbs"])
        macro_totals["fats"] += float(day_macros["total_fats"])

    weekly_recommendations = generate_recommendations(
        {"total_protein": macro_totals["protein"] / max(len(summary), 1),
         "total_carbs": macro_totals["carbs"] / max(len(summary), 1),
         "total_fats": macro_totals["fats"] / max(len(summary), 1)},
        remaining_today["calorie_goal"],
        average,
        {"mood": mood_overview["top_mood"]} if mood_overview["top_mood"] != "No mood data" else None,
    )
    return render_template(
        "weekly_summary.html",
        summary=summary,
        average=average,
        calorie_goal=remaining_today["calorie_goal"],
        days_logged=len(summary),
        total_meals=total_meals,
        start_date=week_ago.isoformat(),
        end_date=today.isoformat(),
        mood_summary_rows=mood_summary_rows,
        mood_overview=mood_overview,
        top_moods=top_moods,
        macro_totals=macro_totals,
        weekly_recommendations=weekly_recommendations,
    )


@analytics_bp.route("/analytics/weekly/<int:user_id>")
@login_required
def weekly_summary_json(user_id):
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(user_id, week_ago.isoformat(), today.isoformat())
    average = get_weekly_average(user_id, week_ago.isoformat(), today.isoformat())
    return jsonify(
        {
            "user_id": user_id,
            "start_date": week_ago.isoformat(),
            "end_date": today.isoformat(),
            "daily_totals": summary,
            "weekly_average": average,
            "days_logged": len(summary),
        }
    )


@analytics_bp.route("/analytics/progress/<int:user_id>")
@login_required
def progress(user_id):
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(user_id, week_ago.isoformat(), today.isoformat())
    remaining_today = get_remaining_calories(user_id, today.isoformat())
    goal = remaining_today["calorie_goal"]
    days_on_track = sum(1 for day in summary if day["total_calories"] <= goal)
    return jsonify(
        {
            "user_id": user_id,
            "calorie_goal": goal,
            "days_logged": len(summary),
            "days_on_track": days_on_track,
            "days_over": len(summary) - days_on_track,
            "today_consumed": remaining_today["consumed"],
            "today_remaining": remaining_today["remaining"],
            "daily_breakdown": summary,
        }
    )
