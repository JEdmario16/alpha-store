from . import tools
import flask
from typing import Optional

from .auth.models import configure as configure_auth_models
from .auth.views import configure as configure_auth_views




def create_app(test_mode: Optional[bool] = False) -> flask.Flask:

    app = flask.Flask(__name__)
    
    if test_mode:
        app.testing = True
   
    # Load config file
    tools.load_config(app)
    tools.setup_loguru(app)

    # Configure auth models
    configure_auth_models(app)

    # Configure auth views
    configure_auth_views(app)

    app.logger.info("App started")
    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True)