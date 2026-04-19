from flask import Blueprint, g, redirect, render_template, request, url_for

from app.controllers.meals import login_required
from app.models.food_entry import search_food_history

foods_bp = Blueprint("foods", __name__)


@foods_bp.route("/foods")
@login_required
def foods_home():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = search_food_history(g.user["user_id"], query)
    return render_template("foods.html", query=query, results=results)
