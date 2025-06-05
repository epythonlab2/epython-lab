from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)

@bp.route('/dcp/dashboard')
def dashboard():
       return render_template("/dcp/dashboard.html")


@bp.route('/salon/dashboard')
def salon_dashboard():
    appointments = [
        {"name": "Emma W.", "time": "9:00 AM", "service": "Haircut"},
        {"name": "Michael B.", "time": "10:30 AM", "service": "Hair Color"},
        {"name": "Olivia G.", "time": "1:00 PM", "service": "Manicure"},
        {"name": "Sophia T.", "time": "3:00 PM", "service": "Facial"},
    ]
    employees = ["Emily R.", "James P.", "Lily S."]
    return render_template("/dashboard/salon_dashboard.html", appointments=appointments, employees=employees)
