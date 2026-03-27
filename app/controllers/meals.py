from flask import Blueprint, render_template

#Creates the blueprint for meal related routes
meals_bp = Blueprint("meals", __name__)

#Home page route
@meals_bp.route("/")
def home():
    return render_template("index.html")

#Show the Add Meal page
@meals_bp.route("/meals/new")
def new_meal():
    return render_template("add_meal.html")

#Temporary meal history page
@meals_bp.route("/meals/history")
def meal_history():
    return "<h2>Meal History Page</h2>"

#Temporary meal details page
@meals_bp.route("/meals/<int:meal_id>")
def meal_details(meal_id):
    return f"<h2>Meal Details Page for Meal #{meal_id}</h2>"







