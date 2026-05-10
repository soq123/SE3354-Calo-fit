from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.meal import get_daily_macros, get_remaining_calories
from app.models.mood import (
    delete_mood_entry,
    get_latest_mood_for_date,
    get_recent_moods,
    get_top_moods,
    get_weekly_mood_summary,
    save_mood_entry,
)
from app.services.insights import generate_recommendations, summarize_weekly_moods

mood_bp = Blueprint("mood", __name__)

VALID_MOODS = {"Happy", "Focused", "Neutral", "Tired", "Stressed"}


def _clean_log_date(raw_date):
    """Return a safe YYYY-MM-DD date string for mood lookup and form reuse."""
    fallback = date.today().isoformat()
    candidate = (raw_date or fallback).strip()
    try:
        return date.fromisoformat(candidate).isoformat()
    except ValueError:
        return fallback


@mood_bp.route("/mood", methods=["GET", "POST"])
@login_required
def mood_tracker():
    today = date.today().isoformat()
    selected_date = _clean_log_date(request.values.get("date") or today)

    if request.method == "POST":
        selected_date = _clean_log_date(request.form.get("log_date") or today)
        mood = request.form.get("mood", "").strip()
        energy_level = request.form.get("energy_level", "").strip()
        mood_notes = request.form.get("mood_notes", "").strip()

        if mood not in VALID_MOODS:
            flash("Please choose a valid mood.", "danger")
        elif not energy_level.isdigit() or int(energy_level) not in range(1, 6):
            flash("Energy level must be between 1 and 5.", "danger")
        else:
            save_mood_entry(
                current_user.id,
                mood,
                int(energy_level),
                mood_notes,
                selected_date,
            )
            flash("Mood entry saved! Your nutrition insight has been updated.", "success")
            return redirect(url_for("mood.mood_tracker", date=selected_date))

    latest_mood = get_latest_mood_for_date(current_user.id, selected_date)
    recent_moods = get_recent_moods(current_user.id, limit=7)

    remaining = get_remaining_calories(current_user.id, selected_date)
    macros = get_daily_macros(current_user.id, selected_date)
    consumed = remaining.get("consumed", 0)
    calorie_goal = remaining.get("calorie_goal", 0)

    recommendations = generate_recommendations(
        macros,
        calorie_goal,
        consumed,
        latest_mood,
    )

    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    weekly_moods = get_weekly_mood_summary(
        current_user.id,
        start_date.isoformat(),
        end_date.isoformat(),
    )

    top_moods = get_top_moods(
        current_user.id,
        start_date.isoformat(),
        end_date.isoformat(),
    )

    weekly_mood_summary = summarize_weekly_moods(weekly_moods, top_moods)

    return render_template(
        "mood.html",
        latest_mood=latest_mood,
        recent_moods=recent_moods,
        recommendations=recommendations,
        selected_date=selected_date,
        weekly_mood_summary=weekly_mood_summary,
        macros=macros,
        calorie_goal=calorie_goal,
        consumed=consumed,
        calories_remaining=remaining.get("remaining", 0),
    )


@mood_bp.route("/mood/delete/<int:mood_id>", methods=["POST"])
@login_required
def delete_mood(mood_id):
    delete_mood_entry(current_user.id, mood_id)
    flash("Mood entry deleted.", "success")
    return redirect(url_for("mood.mood_tracker"))
