from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.models.meal import get_daily_macros, get_remaining_calories
from app.models.mood import add_mood_entry, get_latest_mood_for_date, get_recent_moods
from app.services.insights import generate_recommendations

mood_bp = Blueprint("mood", __name__)


@mood_bp.route("/mood", methods=["GET", "POST"])
@login_required
def mood_tracker():
    today = date.today().isoformat()

    if request.method == "POST":
        mood = request.form.get("mood", "").strip()
        energy_level = request.form.get("energy_level", "").strip()
        mood_notes = request.form.get("mood_notes", "").strip()

        if not mood or not energy_level:
            flash("Please choose a mood and energy level.", "danger")
        else:
            add_mood_entry(current_user.id, mood, int(energy_level), mood_notes, today)
            flash("Mood entry saved!", "success")
            return redirect(url_for("mood.mood_tracker"))

    latest_mood = get_latest_mood_for_date(current_user.id, today)
    recent_moods = get_recent_moods(current_user.id, limit=5)
    remaining = get_remaining_calories(current_user.id, today)
    macros = get_daily_macros(current_user.id, today)
    recommendations = generate_recommendations(
        macros, remaining["calorie_goal"], remaining["consumed"], latest_mood
    )

    return render_template(
        "mood.html",
        latest_mood=latest_mood,
        recent_moods=recent_moods,
        recommendations=recommendations,
    )
