import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import serverless_wsgi
from main import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)