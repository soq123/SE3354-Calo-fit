from flask import Flask

def create_app():
    app = Flask(__name__)

    app.secret_key = "dev_key"

    from app import db
    db.init_app(app)
    
    from app.controllers.meals import meals_bp
    from app.controllers.foods import foods_bp
    from app.controllers.analytics import analytics_bp

    app.register_blueprint(meals_bp)
    app.register_blueprint(foods_bp)
    app.register_blueprint(analytics_bp)

    return app
