import configparser
from typing import Optional
import os
import flask
import loguru
import sys

def load_config(app: Optional[flask.Flask] = None, fp: Optional[str] = None) -> configparser.ConfigParser:
    """
    Load configuration from config.ini file and set it to app.config if app is provided
    """

    fp = fp or os.path.join(os.path.dirname(__file__), "config.ini")
    if os.path.exists(fp):

        # Save config file data to app instance
        config = configparser.ConfigParser()
        config.read(fp)

        if app:
            app.config["cfg"] = config
        return config

    raise FileNotFoundError(f'Cant find config file at {fp}')

def setup_loguru(app: flask.Flask) -> None:

    # Set loguru logger
    app.logger = loguru.logger
    loguru.logger.remove()
    app.logger.add(
        app.config["cfg"]["LOGGING"]["log_file"],
        level=app.config["cfg"]["LOGGING"]["log_level"],
        rotation= "1 MB",
        format="{time} | {level} | {message} | {file}:{line}"
    )

    if not app.testing: # If app is running in test mode, dont add stdout logger
        app.logger.add(sys.stdout, level="DEBUG", format="{time} | {level} | {message} | {file}:{line}")