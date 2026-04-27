import os
import requests
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.food_entry import search_food_history

foods_bp = Blueprint("foods", __name__)

# ── Local nutrition database (per 100g) ───────────────────────────────────────
# Searched first — instant, no API needed. USDA is fallback for unknown foods.
LOCAL_DB = [
    # Fruits
    {"name": "Apple, raw",             "calories": 52,  "protein_g": 0.3, "carbohydrates_total_g": 14.0, "fat_total_g": 0.2},
    {"name": "Banana, raw",            "calories": 89,  "protein_g": 1.1, "carbohydrates_total_g": 23.0, "fat_total_g": 0.3},
    {"name": "Orange, raw",            "calories": 47,  "protein_g": 0.9, "carbohydrates_total_g": 12.0, "fat_total_g": 0.1},
    {"name": "Mango, raw",             "calories": 60,  "protein_g": 0.8, "carbohydrates_total_g": 15.0, "fat_total_g": 0.4},
    {"name": "Grapes, raw",            "calories": 69,  "protein_g": 0.7, "carbohydrates_total_g": 18.0, "fat_total_g": 0.2},
    {"name": "Strawberry, raw",        "calories": 32,  "protein_g": 0.7, "carbohydrates_total_g": 7.7,  "fat_total_g": 0.3},
    {"name": "Blueberry, raw",         "calories": 57,  "protein_g": 0.7, "carbohydrates_total_g": 14.5, "fat_total_g": 0.3},
    {"name": "Watermelon, raw",        "calories": 30,  "protein_g": 0.6, "carbohydrates_total_g": 7.6,  "fat_total_g": 0.2},
    {"name": "Pineapple, raw",         "calories": 50,  "protein_g": 0.5, "carbohydrates_total_g": 13.1, "fat_total_g": 0.1},
    {"name": "Avocado, raw",           "calories": 160, "protein_g": 2.0, "carbohydrates_total_g": 9.0,  "fat_total_g": 15.0},
    {"name": "Peach, raw",             "calories": 39,  "protein_g": 0.9, "carbohydrates_total_g": 9.5,  "fat_total_g": 0.3},
    {"name": "Pear, raw",              "calories": 57,  "protein_g": 0.4, "carbohydrates_total_g": 15.2, "fat_total_g": 0.1},
    {"name": "Kiwi, raw",              "calories": 61,  "protein_g": 1.1, "carbohydrates_total_g": 14.7, "fat_total_g": 0.5},
    {"name": "Cherry, raw",            "calories": 63,  "protein_g": 1.1, "carbohydrates_total_g": 16.0, "fat_total_g": 0.2},
    {"name": "Lemon, raw",             "calories": 29,  "protein_g": 1.1, "carbohydrates_total_g": 9.3,  "fat_total_g": 0.3},
    # Vegetables
    {"name": "Broccoli, raw",          "calories": 34,  "protein_g": 2.8, "carbohydrates_total_g": 7.0,  "fat_total_g": 0.4},
    {"name": "Spinach, raw",           "calories": 23,  "protein_g": 2.9, "carbohydrates_total_g": 3.6,  "fat_total_g": 0.4},
    {"name": "Carrot, raw",            "calories": 41,  "protein_g": 0.9, "carbohydrates_total_g": 10.0, "fat_total_g": 0.2},
    {"name": "Tomato, raw",            "calories": 18,  "protein_g": 0.9, "carbohydrates_total_g": 3.9,  "fat_total_g": 0.2},
    {"name": "Cucumber, raw",          "calories": 15,  "protein_g": 0.7, "carbohydrates_total_g": 3.6,  "fat_total_g": 0.1},
    {"name": "Potato, raw",            "calories": 77,  "protein_g": 2.0, "carbohydrates_total_g": 17.5, "fat_total_g": 0.1},
    {"name": "Sweet potato, raw",      "calories": 86,  "protein_g": 1.6, "carbohydrates_total_g": 20.1, "fat_total_g": 0.1},
    {"name": "Onion, raw",             "calories": 40,  "protein_g": 1.1, "carbohydrates_total_g": 9.3,  "fat_total_g": 0.1},
    {"name": "Garlic, raw",            "calories": 149, "protein_g": 6.4, "carbohydrates_total_g": 33.1, "fat_total_g": 0.5},
    {"name": "Bell pepper, raw",       "calories": 31,  "protein_g": 1.0, "carbohydrates_total_g": 6.0,  "fat_total_g": 0.3},
    {"name": "Lettuce, raw",           "calories": 15,  "protein_g": 1.4, "carbohydrates_total_g": 2.9,  "fat_total_g": 0.2},
    {"name": "Corn, sweet, raw",       "calories": 86,  "protein_g": 3.2, "carbohydrates_total_g": 19.0, "fat_total_g": 1.2},
    {"name": "Peas, green, raw",       "calories": 81,  "protein_g": 5.4, "carbohydrates_total_g": 14.5, "fat_total_g": 0.4},
    {"name": "Cauliflower, raw",       "calories": 25,  "protein_g": 1.9, "carbohydrates_total_g": 5.0,  "fat_total_g": 0.3},
    {"name": "Mushroom, raw",          "calories": 22,  "protein_g": 3.1, "carbohydrates_total_g": 3.3,  "fat_total_g": 0.3},
    {"name": "Zucchini, raw",          "calories": 17,  "protein_g": 1.2, "carbohydrates_total_g": 3.1,  "fat_total_g": 0.3},
    # Grains & Carbs
    {"name": "Oatmeal, cooked",        "calories": 71,  "protein_g": 2.5, "carbohydrates_total_g": 12.0, "fat_total_g": 1.5},
    {"name": "Oats, dry",              "calories": 389, "protein_g": 17.0,"carbohydrates_total_g": 66.0, "fat_total_g": 7.0},
    {"name": "White rice, cooked",     "calories": 130, "protein_g": 2.7, "carbohydrates_total_g": 28.2, "fat_total_g": 0.3},
    {"name": "Brown rice, cooked",     "calories": 112, "protein_g": 2.6, "carbohydrates_total_g": 23.5, "fat_total_g": 0.9},
    {"name": "Pasta, cooked",          "calories": 131, "protein_g": 5.0, "carbohydrates_total_g": 25.1, "fat_total_g": 1.1},
    {"name": "Bread, white",           "calories": 265, "protein_g": 9.0, "carbohydrates_total_g": 49.0, "fat_total_g": 3.2},
    {"name": "Bread, whole wheat",     "calories": 247, "protein_g": 13.0,"carbohydrates_total_g": 41.0, "fat_total_g": 3.4},
    {"name": "Quinoa, cooked",         "calories": 120, "protein_g": 4.4, "carbohydrates_total_g": 21.3, "fat_total_g": 1.9},
    {"name": "Cereal, corn flakes",    "calories": 357, "protein_g": 7.5, "carbohydrates_total_g": 84.0, "fat_total_g": 0.4},
    {"name": "Granola",                "calories": 471, "protein_g": 10.0,"carbohydrates_total_g": 64.0, "fat_total_g": 20.0},
    {"name": "Tortilla, flour",        "calories": 312, "protein_g": 8.0, "carbohydrates_total_g": 54.0, "fat_total_g": 7.0},
    {"name": "Bagel",                  "calories": 250, "protein_g": 10.0,"carbohydrates_total_g": 48.0, "fat_total_g": 1.6},
    {"name": "Croissant",              "calories": 406, "protein_g": 8.2, "carbohydrates_total_g": 46.0, "fat_total_g": 21.0},
    # Proteins — Meat & Seafood
    {"name": "Chicken breast, cooked", "calories": 165, "protein_g": 31.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 3.6},
    {"name": "Chicken thigh, cooked",  "calories": 209, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 11.0},
    {"name": "Beef, ground, cooked",   "calories": 254, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 17.0},
    {"name": "Beef steak, grilled",    "calories": 271, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 18.0},
    {"name": "Salmon, cooked",         "calories": 208, "protein_g": 20.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 13.0},
    {"name": "Tuna, canned in water",  "calories": 116, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 1.0},
    {"name": "Shrimp, cooked",         "calories": 99,  "protein_g": 24.0,"carbohydrates_total_g": 0.2,  "fat_total_g": 0.3},
    {"name": "Turkey breast, cooked",  "calories": 135, "protein_g": 30.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 1.0},
    {"name": "Pork chop, cooked",      "calories": 231, "protein_g": 25.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 14.0},
    {"name": "Lamb, cooked",           "calories": 258, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 16.0},
    {"name": "Egg, whole, cooked",     "calories": 155, "protein_g": 13.0,"carbohydrates_total_g": 1.1,  "fat_total_g": 11.0},
    {"name": "Egg white, cooked",      "calories": 52,  "protein_g": 11.0,"carbohydrates_total_g": 0.7,  "fat_total_g": 0.2},
    # Dairy
    {"name": "Milk, whole",            "calories": 61,  "protein_g": 3.2, "carbohydrates_total_g": 4.8,  "fat_total_g": 3.3},
    {"name": "Milk, skimmed",          "calories": 34,  "protein_g": 3.4, "carbohydrates_total_g": 5.0,  "fat_total_g": 0.1},
    {"name": "Greek yogurt, plain",    "calories": 59,  "protein_g": 10.0,"carbohydrates_total_g": 3.6,  "fat_total_g": 0.4},
    {"name": "Yogurt, plain",          "calories": 63,  "protein_g": 5.3, "carbohydrates_total_g": 7.0,  "fat_total_g": 1.6},
    {"name": "Cheddar cheese",         "calories": 403, "protein_g": 25.0,"carbohydrates_total_g": 1.3,  "fat_total_g": 33.0},
    {"name": "Mozzarella cheese",      "calories": 280, "protein_g": 28.0,"carbohydrates_total_g": 2.2,  "fat_total_g": 17.0},
    {"name": "Butter",                 "calories": 717, "protein_g": 0.9, "carbohydrates_total_g": 0.1,  "fat_total_g": 81.0},
    {"name": "Cream cheese",           "calories": 342, "protein_g": 6.2, "carbohydrates_total_g": 4.1,  "fat_total_g": 34.0},
    {"name": "Ice cream, vanilla",     "calories": 207, "protein_g": 3.5, "carbohydrates_total_g": 24.0, "fat_total_g": 11.0},
    # Legumes & Plant Protein
    {"name": "Lentils, cooked",        "calories": 116, "protein_g": 9.0, "carbohydrates_total_g": 20.0, "fat_total_g": 0.4},
    {"name": "Chickpeas, cooked",      "calories": 164, "protein_g": 8.9, "carbohydrates_total_g": 27.0, "fat_total_g": 2.6},
    {"name": "Black beans, cooked",    "calories": 132, "protein_g": 8.9, "carbohydrates_total_g": 24.0, "fat_total_g": 0.5},
    {"name": "Kidney beans, cooked",   "calories": 127, "protein_g": 8.7, "carbohydrates_total_g": 23.0, "fat_total_g": 0.5},
    {"name": "Tofu, firm",             "calories": 76,  "protein_g": 8.0, "carbohydrates_total_g": 1.9,  "fat_total_g": 4.8},
    {"name": "Edamame, cooked",        "calories": 121, "protein_g": 11.9,"carbohydrates_total_g": 8.9,  "fat_total_g": 5.2},
    # Nuts & Seeds
    {"name": "Almonds",                "calories": 579, "protein_g": 21.0,"carbohydrates_total_g": 22.0, "fat_total_g": 50.0},
    {"name": "Walnuts",                "calories": 654, "protein_g": 15.0,"carbohydrates_total_g": 14.0, "fat_total_g": 65.0},
    {"name": "Cashews",                "calories": 553, "protein_g": 18.0,"carbohydrates_total_g": 30.0, "fat_total_g": 44.0},
    {"name": "Peanuts",                "calories": 567, "protein_g": 26.0,"carbohydrates_total_g": 16.0, "fat_total_g": 49.0},
    {"name": "Peanut butter",          "calories": 588, "protein_g": 25.0,"carbohydrates_total_g": 20.0, "fat_total_g": 50.0},
    {"name": "Chia seeds",             "calories": 486, "protein_g": 17.0,"carbohydrates_total_g": 42.0, "fat_total_g": 31.0},
    {"name": "Sunflower seeds",        "calories": 584, "protein_g": 21.0,"carbohydrates_total_g": 20.0, "fat_total_g": 51.0},
    # Fast food & Common Meals
    {"name": "Pizza, cheese",          "calories": 266, "protein_g": 11.0,"carbohydrates_total_g": 33.0, "fat_total_g": 10.0},
    {"name": "Burger, beef",           "calories": 295, "protein_g": 17.0,"carbohydrates_total_g": 24.0, "fat_total_g": 14.0},
    {"name": "French fries",           "calories": 312, "protein_g": 3.4, "carbohydrates_total_g": 41.0, "fat_total_g": 15.0},
    {"name": "Hot dog",                "calories": 290, "protein_g": 11.0,"carbohydrates_total_g": 22.0, "fat_total_g": 17.0},
    {"name": "Sandwich, turkey",       "calories": 218, "protein_g": 16.0,"carbohydrates_total_g": 28.0, "fat_total_g": 4.3},
    # Drinks
    {"name": "Orange juice",           "calories": 45,  "protein_g": 0.7, "carbohydrates_total_g": 10.4, "fat_total_g": 0.2},
    {"name": "Apple juice",            "calories": 46,  "protein_g": 0.1, "carbohydrates_total_g": 11.4, "fat_total_g": 0.1},
    {"name": "Coca-Cola",              "calories": 42,  "protein_g": 0.0, "carbohydrates_total_g": 10.6, "fat_total_g": 0.0},
    {"name": "Coffee, black",          "calories": 2,   "protein_g": 0.3, "carbohydrates_total_g": 0.0,  "fat_total_g": 0.0},
    {"name": "Coffee with milk",       "calories": 13,  "protein_g": 0.6, "carbohydrates_total_g": 1.0,  "fat_total_g": 0.5},
    {"name": "Green tea",              "calories": 1,   "protein_g": 0.0, "carbohydrates_total_g": 0.2,  "fat_total_g": 0.0},
    # Snacks & Sweets
    {"name": "Chocolate, dark",        "calories": 546, "protein_g": 5.0, "carbohydrates_total_g": 60.0, "fat_total_g": 31.0},
    {"name": "Chocolate, milk",        "calories": 535, "protein_g": 8.0, "carbohydrates_total_g": 59.0, "fat_total_g": 30.0},
    {"name": "Potato chips",           "calories": 536, "protein_g": 7.0, "carbohydrates_total_g": 53.0, "fat_total_g": 35.0},
    {"name": "Crackers",               "calories": 424, "protein_g": 9.0, "carbohydrates_total_g": 68.0, "fat_total_g": 13.0},
    {"name": "Popcorn",                "calories": 375, "protein_g": 11.0,"carbohydrates_total_g": 74.0, "fat_total_g": 4.0},
    {"name": "Protein bar",            "calories": 390, "protein_g": 30.0,"carbohydrates_total_g": 40.0, "fat_total_g": 10.0},
    {"name": "Honey",                  "calories": 304, "protein_g": 0.3, "carbohydrates_total_g": 82.0, "fat_total_g": 0.0},
    # Oils & Condiments
    {"name": "Olive oil",              "calories": 884, "protein_g": 0.0, "carbohydrates_total_g": 0.0,  "fat_total_g": 100.0},
    {"name": "Mayonnaise",             "calories": 680, "protein_g": 1.0, "carbohydrates_total_g": 0.6,  "fat_total_g": 75.0},
    {"name": "Ketchup",                "calories": 112, "protein_g": 1.3, "carbohydrates_total_g": 27.0, "fat_total_g": 0.1},
    {"name": "Hummus",                 "calories": 166, "protein_g": 8.0, "carbohydrates_total_g": 14.0, "fat_total_g": 10.0},
    {"name": "Salsa",                  "calories": 36,  "protein_g": 1.6, "carbohydrates_total_g": 7.4,  "fat_total_g": 0.2},
]

# Simple in-memory USDA cache — avoids duplicate API calls this session
_usda_cache: dict = {}


def search_local(query: str) -> list:
    """Case-insensitive substring search against the local database."""
    q = query.lower().strip()
    matches = [f for f in LOCAL_DB if q in f["name"].lower()]
    # Sort: exact-start matches first
    matches.sort(key=lambda f: (0 if f["name"].lower().startswith(q) else 1, f["name"]))
    return matches[:5]


def search_usda(query: str) -> list:
    """Call USDA FoodData Central, with per-session caching."""
    if query in _usda_cache:
        return _usda_cache[query]

    api_key = os.environ.get("USDA_FDC_API_KEY", "DEMO_KEY")
    try:
        resp = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={"query": query, "api_key": api_key,
                    "dataType": "SR Legacy,Foundation", "pageSize": 5},
            timeout=8,
        )
        if resp.status_code == 429:
            return []          # rate-limited — silently skip
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return []

    IDS  = {1008: "calories", 1003: "protein_g", 1005: "carbohydrates_total_g", 1004: "fat_total_g"}
    NUMS = {"208": "calories", "203": "protein_g", "205": "carbohydrates_total_g", "204": "fat_total_g"}

    results = []
    for food in data.get("foods", []):
        vals = {v: 0.0 for v in IDS.values()}
        for n in food.get("foodNutrients", []):
            key = IDS.get(n.get("nutrientId")) or NUMS.get(str(n.get("nutrientNumber", "")))
            if key:
                try:
                    vals[key] = float(n.get("value", 0))
                except (TypeError, ValueError):
                    pass
        results.append({
            "name": food.get("description", query).title(),
            "calories": round(vals["calories"]),
            "protein_g": round(vals["protein_g"], 1),
            "carbohydrates_total_g": round(vals["carbohydrates_total_g"], 1),
            "fat_total_g": round(vals["fat_total_g"], 1),
        })

    _usda_cache[query] = results
    return results


# ─────────────────────────────────────────────────────────────────────────────

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

    # 1. Local DB first (instant, no rate limits)
    results = search_local(query)

    # 2. Fall back to USDA only when local has no hits
    if not results:
        results = search_usda(query)

    if not results:
        return jsonify({"error": f"No results found for '{query}'. Try a different spelling."}), 404

    return jsonify({"results": results})
