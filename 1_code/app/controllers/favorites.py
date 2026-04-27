from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.favorites import get_favorites, add_favorite, delete_favorite
from app.models.meal_limit import set_limit, get_limits

fav_bp = Blueprint("favorites", __name__)


@fav_bp.route("/api/favorites", methods=["GET"])
@login_required
def list_favorites():
    return jsonify(get_favorites(current_user.id))


@fav_bp.route("/api/favorites", methods=["POST"])
@login_required
def create_favorite():
    data = request.get_json(silent=True) or {}
    food_name = (data.get("food_name") or "").strip()
    if not food_name:
        return jsonify({"status": "error", "message": "food_name is required"}), 400
    fav_id = add_favorite(
        current_user.id,
        food_name,
        float(data.get("calories") or 0),
        float(data.get("protein") or 0),
        float(data.get("carbs") or 0),
        float(data.get("fats") or 0),
        float(data.get("iron") or 0),
        float(data.get("zinc") or 0),
        float(data.get("calcium") or 0),
        data.get("meal_type") or None,
    )
    return jsonify({"status": "ok", "fav_id": fav_id})


@fav_bp.route("/api/favorites/<int:fav_id>", methods=["DELETE"])
@login_required
def remove_favorite(fav_id):
    delete_favorite(fav_id, current_user.id)
    return jsonify({"status": "ok"})


@fav_bp.route("/api/limits", methods=["POST"])
@login_required
def save_limits():
    data = request.get_json(silent=True) or {}
    for meal_type in ("Breakfast", "Lunch", "Dinner", "Snack"):
        val = data.get(meal_type, 0)
        try:
            set_limit(current_user.id, meal_type, int(val))
        except (ValueError, TypeError):
            pass
    return jsonify({"status": "ok"})


@fav_bp.route("/api/limits", methods=["GET"])
@login_required
def fetch_limits():
    return jsonify(get_limits(current_user.id))
