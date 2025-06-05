from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)

@bp.route('/dcp/dashboard')
def dashboard():
       return render_template("/dcp/dashboard.html")


@bp.route('/dcp/admin/topics')
def admin_manage_topics():

    return render_template("/dcp/tutorials/manage_topics.html")
