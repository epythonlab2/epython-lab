from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template("index.html" )

@bp.route('/python/')
def introduction():
    return render_template("/tutorial/introduction.html" )