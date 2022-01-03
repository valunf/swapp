from flask import Flask
from app.config import *
app = Flask(__name__)
app.secret_key = b'_as8*93f]\ner\56ddfwpotmza'
if app.env == 'production':
    app.config.from_object(ProductionConfig())
elif app.env == 'development':
    app.config.from_object(DevelopmentConfig())
elif app.env == 'testing':
    app.config.from_object(TestingConfig())
else:
    raise EnvironmentError("FLASK_ENV not defined!")
# noinspection PyUnresolvedReferences
from app import views
