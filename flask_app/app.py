from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import recommend_time
    app.register_blueprint(recommend_time)

    return app