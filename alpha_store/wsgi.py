import sys
import os

# Add the parent directory to the path so we can import the alpha_store package 
# Differently from ``flask run`` command, that import the current package and calls __init__.py, waitress doesn't do that
# So we need to add the parent directory to the path and import the alpha_store package
# (likely gunicorn does the same)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpha_store.main import create_app

app = application = create_app()