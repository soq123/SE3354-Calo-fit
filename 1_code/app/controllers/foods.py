import os
import requests
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.food_entry import search_food_history

foods_bp = Blueprint("foods", __name__)


@foods_bp.route("/foods")
@login_required
def foods_home():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = search_food_history(current_user.id, query)
    return render_template("foods.html", query=query, results=results)

@foods_bp.route("/api/nutrition")
@login_required
def nutrition_lookup():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400

    api_key = current_app.config.get("USDA_FDC_API_KEY") or os.environ.get("USDA_FDC_API_KEY", "DEMO_KEY")

    try:
        resp = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "query": query,
                "api_key": api_key,
                "dataType": "SR Legacy,Foundation",
                "pageSize": 5,
            },
            timeout=8
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        current_app.logger.error(f"[nutrition] USDA request failed: {e}")
        return jsonify({"error": "Failed to reach USDA nutrition database."}), 502

    foods = data.get("foods", [])
    if not foods:
        return jsonify({"error": f"No nutrition data found for '{query}'."}), 404

    # Match by nutrientId (int) or nutrientNumber (string) — the search API is inconsistent
    NUTRIENT_IDS = {1008: "calories", 1003: "protein_g", 1005: "carbohydrates_total_g", 1004: "fat_total_g"}
    NUTRIENT_NUMS = {"208": "calories", "203": "protein_g", "205": "carbohydrates_total_g", "204": "fat_total_g"}

    def extract_nutrients(food):
        nutrients = {label: 0.0 for label in NUTRIENT_IDS.values()}
        for n in food.get("foodNutrients", []):
            label = NUTRIENT_IDS.get(n.get("nutrientId")) or NUTRIENT_NUMS.get(str(n.get("nutrientNumber", "")))
            if label:
                try:
                    nutrients[label] = float(n.get("value", 0))
                except (TypeError, ValueError):
                    pass
        return {
            "name": food.get("description", query),
            "calories": round(nutrients["calories"]),
            "protein_g": round(nutrients["protein_g"], 1),
            "carbohydrates_total_g": round(nutrients["carbohydrates_total_g"], 1),
            "fat_total_g": round(nutrients["fat_total_g"], 1),
        }

    return jsonify({"results": [extract_nutrients(f) for f in foods]})
