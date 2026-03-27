from flask import Blueprint

foods_bp = Blueprint("foods", __name__)


#Show the Food page
@foods_bp.route("/foods")
def foods_home():
    return "<h2>Foods Page</h2>"