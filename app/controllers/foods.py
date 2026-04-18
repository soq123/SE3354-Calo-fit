from flask import Blueprint, render_template, request
from app.models.food_entry import search_food_history

foods_bp = Blueprint("foods", __name__)

USER_ID = 1

@foods_bp.route("/foods")
def foods_home():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = search_food_history(USER_ID, query)
    return render_template("foods.html", query=query, results=results)
