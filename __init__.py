from flask import Flask
from app import configuration
application=Flask(__name__)
application.config.from_object(configuration)

from app import views
from app.sender import sender_views
from app import dashboard_views

