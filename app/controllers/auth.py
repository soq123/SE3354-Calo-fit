from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.models.user import create_user, get_user_by_email, verify_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.get("user"):
        return redirect(url_for("meals.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = verify_user(email, password)
        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user["user_id"]
        flash("Welcome back!", "success")
        return redirect(url_for("meals.home"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if g.get("user"):
        return redirect(url_for("meals.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        calorie_goal = request.form.get("calorie_goal", 2000)

        if not username or not email or not password:
            flash("Please complete all required fields.", "danger")
            return render_template("register.html", username=username, email=email, calorie_goal=calorie_goal)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", username=username, email=email, calorie_goal=calorie_goal)

        if get_user_by_email(email):
            flash("An account with that email already exists.", "danger")
            return render_template("register.html", username=username, email=email, calorie_goal=calorie_goal)

        try:
            user_id = create_user(username, email, password, int(calorie_goal or 2000))
        except Exception:
            flash("Unable to create account. Please try a different username or email.", "danger")
            return render_template("register.html", username=username, email=email, calorie_goal=calorie_goal)

        session.clear()
        session["user_id"] = user_id
        flash("Account created successfully!", "success")
        return redirect(url_for("meals.home"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
