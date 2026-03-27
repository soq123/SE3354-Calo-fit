from flask import Flask

def create_app():
    app = Flask(__name__)

    app.secret_key = "dev_key"

    from app.controllers.meals import meals_bp
    from app.controllers.foods import foods_bp

    app.register_blueprint(meals_bp)
    app.register_blueprint(foods_bp)

    return app