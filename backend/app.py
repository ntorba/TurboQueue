import os 
import requests
import time 
from pathlib import Path 
from dotenv import load_dotenv
from flask import Flask, render_template

from .extensions import db, turbo, cors
from .models import Song, Party

BASE_DIR = Path(__file__).parent.parent 

def create_app(deploy_mode="Development"):
    load_dotenv()
    deploy_mode = deploy_mode if deploy_mode is not None else os.environ.get("DEPLOY_MODE", "Development")
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="/static/")
    config_module = f'config.{deploy_mode}Config'
    print(f"running with {config_module} config")
    app.config.from_object(config_module)
    app.config["CORS_HEADERS"] = "Content-Type"
    app.config.update(
        {
            "WEBPACK_LOADER": {
                "MANIFEST_FILE": os.path.join(BASE_DIR, "frontend/build/manifest.json"),
            }
        }
    )
    from webpack_boilerplate.config import setup_jinja2_ext
    setup_jinja2_ext(app) 
    from .views import spotify_oauth_blueprint
    app.register_blueprint(spotify_oauth_blueprint)
    from .views import party_blueprint
    app.register_blueprint(party_blueprint)
    cors.init_app(app)
    turbo.init_app(app)
    db.init_app(app)

    @app.cli.command("webpack_init")
    def webpack_init():
        from cookiecutter.main import cookiecutter
        import webpack_boilerplate

        pkg_path = os.path.dirname(webpack_boilerplate.__file__)
        cookiecutter(pkg_path, directory="frontend_template")

    return app 