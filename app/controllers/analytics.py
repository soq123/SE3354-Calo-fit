from flask import Blueprint, jsonify
from datetime import date, timedelta
from app.models.meal import (
    get_daily_total,
    get_daily_macros,
    get_remaining_calories,
    get_weekly_summary,
    get_weekly_average
)
