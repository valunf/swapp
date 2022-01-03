#!venv/bin/python3
# -*- coding: utf-8 -*-
from app import app

BACKEND_URI = app.config['BACKEND_URI']

app.run(host=app.config['FLASK_LISTEN_IP'],
        port=app.config['FLASK_LISTEN_PORT'],
        debug=app.config['DEBUG'])
