from flask import Flask, session, g
from app.models.user import get_user_by_id


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev_key"

    from app import db
    db.init_app(app)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = get_user_by_id(user_id) if user_id else None

    from app.controllers.meals import meals_bp
    from app.controllers.foods import foods_bp
    from app.controllers.analytics import analytics_bp
    from app.controllers.mood import mood_bp
    from app.controllers.auth import auth_bp

    app.register_blueprint(meals_bp)
    app.register_blueprint(foods_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(auth_bp)

    return app
