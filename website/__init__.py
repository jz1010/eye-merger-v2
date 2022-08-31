#!/usr/bin/env python3
from flask import Flask, flash, redirect, render_template, request, session, abort
import os




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']=os.urandom(12)

    from .views import views


    app.register_blueprint(views, url_prefix='/')


    return app


