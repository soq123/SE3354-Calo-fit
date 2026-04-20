from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlite3 import IntegrityError
from app.models.user import get_user_by_email, get_user_by_username, create_user, verify_user_email, get_user_by_id, update_password

auth_bp = Blueprint("auth", __name__)

TOKEN_SALT = "email-verify"
TOKEN_MAX_AGE = 86400  # 24 hours

RESET_SALT = "password-reset"
RESET_MAX_AGE = 3600  # 1 hour


def _serializer():
    return URLSafeTimedSerializer(current_app.secret_key)


def _send_verification_email(user_email):
    """Send a verification email. Falls back to logging if mail is not configured."""
    from app import mail
    from flask_mail import Message

    token = _serializer().dumps(user_email, salt=TOKEN_SALT)
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    if not current_app.config.get("MAIL_USERNAME"):
        # No mail configured — print to terminal for development
        current_app.logger.info(
            f"[auth] Email verification link for {user_email}:\n{verify_url}"
        )
        return

    msg = Message(
        subject="Verify your CaloFit email",
        recipients=[user_email],
        body=(
            f"Welcome to CaloFit!\n\n"
            f"Please verify your email address by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you did not create an account, you can ignore this email."
        ),
    )
    mail.send(msg)


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("meals.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        try:
            calorie_goal = max(1000, int(request.form.get("calorie_goal", 2000)))
        except (ValueError, TypeError):
            calorie_goal = 2000

        # Server-side validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        # Check uniqueness
        if get_user_by_username(username):
            flash("That username is already taken.", "danger")
            return render_template("auth/register.html")

        if get_user_by_email(email):
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html")

        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )
        try:
            create_user(username, email, password_hash, calorie_goal)
        except IntegrityError:
            flash("That username or email is already taken.", "danger")
            return render_template("auth/register.html")

        _send_verification_email(email)

        flash("Account created! Please check your email to verify your account.", "success")
        return redirect(url_for("auth.verify_sent"))

    return render_template("auth/register.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("meals.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember_me"))

        user = get_user_by_email(email)

        # Always run check_password_hash to prevent timing oracle attacks
        # Use a dummy hash when user is not found
        dummy_hash = "pbkdf2:sha256:260000$x$" + "a" * 64
        stored_hash = user.password_hash if user else dummy_hash
        password_valid = check_password_hash(stored_hash, password)

        if not user or not password_valid:
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if not user.email_verified:
            flash(
                "Please verify your email before logging in. "
                '<a href="/resend-verification?email=' + email + '">Resend verification email</a>',
                "warning"
            )
            return render_template("auth/login.html")

        login_user(user, remember=remember)

        # Safe redirect: only allow relative internal URLs
        next_page = request.args.get("next", "")
        if next_page and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)
        return redirect(url_for("meals.home"))

    return render_template("auth/login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── Email verification ────────────────────────────────────────────────────────

@auth_bp.route("/verify/<token>")
def verify_email(token):
    try:
        email = _serializer().loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
    except SignatureExpired:
        flash("Verification link has expired. Request a new one below.", "warning")
        return render_template("auth/verify_failed.html")
    except BadSignature:
        flash("Invalid verification link.", "danger")
        return render_template("auth/verify_failed.html")

    user = get_user_by_email(email)
    if not user:
        flash("Account not found.", "danger")
        return render_template("auth/verify_failed.html")

    if user.email_verified:
        flash("Your email is already verified. Please log in.", "info")
        return redirect(url_for("auth.login"))

    verify_user_email(user.id)
    flash("Email verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/verify-sent")
def verify_sent():
    return render_template("auth/verify_sent.html")


@auth_bp.route("/resend-verification")
def resend_verification():
    email = request.args.get("email", "").strip().lower()
    if not email:
        flash("No email address provided.", "danger")
        return redirect(url_for("auth.login"))

    user = get_user_by_email(email)
    # Always show the same message to prevent user enumeration
    if user and not user.email_verified:
        _send_verification_email(email)

    flash("If that email is registered and unverified, a new link has been sent.", "info")
    return redirect(url_for("auth.verify_sent"))


# ── Forgot / Reset Password ────────────────────────────────────────────────────

def _send_reset_email(user_email):
    """Send a password reset email. Falls back to logging if mail is not configured."""
    from app import mail
    from flask_mail import Message

    token = _serializer().dumps(user_email, salt=RESET_SALT)
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.info(
            f"[auth] Password reset link for {user_email}:\n{reset_url}"
        )
        return

    msg = Message(
        subject="Reset your CaloFit password",
        recipients=[user_email],
        body=(
            f"Hi,\n\n"
            f"You requested a password reset for your CaloFit account.\n\n"
            f"Click the link below to choose a new password:\n\n"
            f"{reset_url}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"If you did not request this, you can ignore this email."
        ),
    )
    mail.send(msg)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("meals.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if email:
            user = get_user_by_email(email)
            if user:
                _send_reset_email(email)
        # Always show the same message to prevent user enumeration
        flash("If that email is associated with an account, a reset link has been sent.", "info")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("meals.home"))

    try:
        email = _serializer().loads(token, salt=RESET_SALT, max_age=RESET_MAX_AGE)
    except SignatureExpired:
        flash("This password reset link has expired. Please request a new one.", "warning")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Invalid password reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = get_user_by_email(email)
    if not user:
        flash("Account not found.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/reset_password.html", token=token)

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html", token=token)

        password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
        update_password(user.id, password_hash)
        flash("Your password has been reset. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
