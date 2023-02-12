import flask

from alpha_store import tools
from alpha_store.models import configure as configure_auth_models
from alpha_store.auth.views import configure as configure_auth_views
from alpha_store.catalog.views import configure as configure_catalog_views
from alpha_store.analytics.views import configure as configure_analytics_views

from typing import Optional

def create_app(test_mode: Optional[bool] = False) -> flask.Flask:

    app = flask.Flask(__name__)

    # set the app secret key
    app.secret_key = "super hiper hidden "

    if test_mode:
        app.testing = True

    # Load config file
    tools.load_config(app)
    tools.setup_loguru(app)

    # Configure models
    configure_auth_models(app)

    # Configure views
    configure_auth_views(app)
    configure_catalog_views(app)
    configure_analytics_views(app)

    app.logger.info("App started")

    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True)
