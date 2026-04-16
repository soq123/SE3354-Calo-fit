from flask import Blueprint, jsonify
from datetime import date, timedelta
from app.models.meal import (
    get_daily_total,
    get_daily_macros,
    get_remaining_calories,
    get_weekly_summary,
    get_weekly_average
)

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics/daily/<int:user_id>")
def daily_summary(user_id):
    today = date.today().isoformat()
    total = get_daily_total(user_id, today)
    macros = get_daily_macros(user_id, today)
    remaining = get_remaining_calories(user_id, today)
    return jsonify({
        "user_id": user_id,
        "date": today,
        "total_calories": total,
        "macros": macros,
        "calorie_goal": remaining["calorie_goal"],
        "calories_remaining": remaining["remaining"]
    })

@analytics_bp.route("/analytics/daily/<int:user_id>/<log_date>")
def daily_summary_by_date(user_id, log_date):
    total = get_daily_total(user_id, log_date)
    macros = get_daily_macros(user_id, log_date)
    remaining = get_remaining_calories(user_id, log_date)
    return jsonify({
        "user_id": user_id,
        "date": log_date,
        "total_calories": total,
        "macros": macros,
        "calorie_goal": remaining["calorie_goal"],
        "calories_remaining": remaining["remaining"]
    })

@analytics_bp.route("/analytics/weekly/<int:user_id>")
def weekly_summary(user_id):
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(user_id, week_ago.isoformat(), today.isoformat())
    average = get_weekly_average(user_id, week_ago.isoformat(), today.isoformat())
    return jsonify({
        "user_id": user_id,
        "start_date": week_ago.isoformat(),
        "end_date": today.isoformat(),
        "daily_totals": summary,
        "weekly_average": average,
        "days_logged": len(summary)
    })

@analytics_bp.route("/analytics/progress/<int:user_id>")
def progress(user_id):
    today = date.today()
    week_ago = today - timedelta(days=6)
    summary = get_weekly_summary(user_id, week_ago.isoformat(), today.isoformat())
    remaining_today = get_remaining_calories(user_id, today.isoformat())
    goal = remaining_today["calorie_goal"]
    days_on_track = sum(1 for day in summary if day["total_calories"] <= goal)
    return jsonify({
        "user_id": user_id,
        "calorie_goal": goal,
        "days_logged": len(summary),
        "days_on_track": days_on_track,
        "days_over": len(summary) - days_on_track,
        "today_consumed": remaining_today["consumed"],
        "today_remaining": remaining_today["remaining"],
        "daily_breakdown": summary
    })
