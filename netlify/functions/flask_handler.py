import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

import serverless_wsgi
import json
from main import app

def handler(event, context):
    try:
        return serverless_wsgi.handle_request(app, event, context)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }