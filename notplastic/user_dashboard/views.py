from flask import Blueprint, request, abort, send_file, redirect, url_for, render_template, make_response, session, current_app

mod = Blueprint('user_dashboard',
                __name__,
                url_prefix='/user',
                template_folder='templates',
                static_folder='static')

@mod.route('/')
def index():
    return render_template('index.html')
