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
