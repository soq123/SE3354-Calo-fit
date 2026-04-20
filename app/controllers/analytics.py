from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.models.meal import (
    get_daily_total,
    get_daily_macros,
    get_remaining_calories,
    get_weekly_summary,
    get_weekly_average
)
from app.models.mood import get_weekly_mood_summary, get_top_moods
from app.services.insights import summarize_weekly_moods

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/daily")
@login_required
def daily_summary():
    today = date.today().isoformat()
    total = get_daily_total(current_user.id, today)
    macros = get_daily_macros(current_user.id, today)
    remaining = get_remaining_calories(current_user.id, today)
    return jsonify({
        "date": today,
        "total_calories": total,
        "macros": macros,
        "calorie_goal": remaining["calorie_goal"],
        "calories_remaining": remaining["remaining"]
    })


@analytics_bp.route("/analytics/daily/<log_date>")
@login_required
def daily_summary_by_date(log_date):
    total = get_daily_total(current_user.id, log_date)
    macros = get_daily_macros(current_user.id, log_date)
    remaining = get_remaining_calories(current_user.id, log_date)
    return jsonify({
        "date": log_date,
        "total_calories": total,
        "macros": macros,
        "calorie_goal": remaining["calorie_goal"],
        "calories_remaining": remaining["remaining"]
    })


@analytics_bp.route("/analytics/weekly")
@login_required
def weekly_summary():
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(current_user.id, week_ago.isoformat(), today.isoformat())
    average = get_weekly_average(current_user.id, week_ago.isoformat(), today.isoformat())
    remaining_today = get_remaining_calories(current_user.id, today.isoformat())
    calorie_goal = remaining_today["calorie_goal"]
    total_meals = sum(day["meal_count"] for day in summary)
    mood_rows = get_weekly_mood_summary(current_user.id, week_ago.isoformat(), today.isoformat())
    top_moods = get_top_moods(current_user.id, week_ago.isoformat(), today.isoformat())
    mood_summary = summarize_weekly_moods(mood_rows, top_moods)
    return render_template(
        "weekly_summary.html",
        summary=summary,
        average=average,
        calorie_goal=calorie_goal,
        days_logged=len(summary),
        total_meals=total_meals,
        start_date=week_ago.isoformat(),
        end_date=today.isoformat(),
        mood_summary=mood_summary
    )


@analytics_bp.route("/analytics/weekly/json")
@login_required
def weekly_summary_json():
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(current_user.id, week_ago.isoformat(), today.isoformat())
    average = get_weekly_average(current_user.id, week_ago.isoformat(), today.isoformat())
    return jsonify({
        "start_date": week_ago.isoformat(),
        "end_date": today.isoformat(),
        "daily_totals": summary,
        "weekly_average": average,
        "days_logged": len(summary)
    })


@analytics_bp.route("/analytics/progress")
@login_required
def progress():
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(current_user.id, week_ago.isoformat(), today.isoformat())
    remaining_today = get_remaining_calories(current_user.id, today.isoformat())
    goal = remaining_today["calorie_goal"]
    days_on_track = sum(1 for day in summary if day["total_calories"] <= goal)
    return jsonify({
        "calorie_goal": goal,
        "days_logged": len(summary),
        "days_on_track": days_on_track,
        "days_over": len(summary) - days_on_track,
        "today_consumed": remaining_today["consumed"],
        "today_remaining": remaining_today["remaining"],
        "daily_breakdown": summary
    })
