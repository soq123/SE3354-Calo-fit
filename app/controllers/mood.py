from flask import Blueprint, render_template, request, flash, redirect, url_for

mood_bp = Blueprint("mood", __name__)

@mood_bp.route("/mood", methods=["GET", "POST"])
def mood_tracker():
    if request.method == "POST":
        # TODO: save mood data to DB
        flash("Mood entry saved!", "success")
        return redirect(url_for("mood.mood_tracker"))
    return render_template("mood.html")
