from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config.config import Config

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import get_user_by_id
    return get_user_by_id(user_id)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config.get("SECRET_KEY") or "dev_key"

    from app import db
    db.init_app(app)

    mail.init_app(app)
    login_manager.init_app(app)

    from app.controllers.auth import auth_bp
    from app.controllers.meals import meals_bp
    from app.controllers.foods import foods_bp
    from app.controllers.analytics import analytics_bp
    from app.controllers.mood import mood_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(meals_bp)
    app.register_blueprint(foods_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(mood_bp)

    return app
