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

    try:
        resp = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 8,
                "fields": "product_name,nutriments",
                "sort_by": "unique_scans_n",
            },
            timeout=10,
            headers={"User-Agent": "CaloFit/1.0 (nutrition tracking app)"},
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        current_app.logger.error(f"[nutrition] Open Food Facts request failed: {e}")
        return jsonify({"error": "Could not reach the nutrition database. Try again."}), 502

    products = data.get("products", [])
    results = []
    for p in products:
        name = (p.get("product_name") or "").strip()
        if not name:
            continue
        n = p.get("nutriments", {})
        cal = n.get("energy-kcal_100g") or n.get("energy-kcal") or 0
        try:
            cal = float(cal)
        except (TypeError, ValueError):
            cal = 0.0
        if cal <= 0:
            continue
        results.append({
            "name": name,
            "calories": round(cal),
            "protein_g": round(float(n.get("proteins_100g") or 0), 1),
            "carbohydrates_total_g": round(float(n.get("carbohydrates_100g") or 0), 1),
            "fat_total_g": round(float(n.get("fat_100g") or 0), 1),
        })
        if len(results) == 5:
            break

    if not results:
        return jsonify({"error": f"No nutrition data found for '{query}'. Try a different spelling."}), 404

    return jsonify({"results": results})
