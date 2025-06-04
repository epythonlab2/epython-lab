from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)

@bp.route('/admin/dashboard')
def admin_dashboard():
    salons = [
        {"name": "Glow & Go", "rating": 4.9},
        {"name": "Luxe Looks", "rating": 4.8},
        {"name": "Radiant You", "rating": 4.7},
    ]
    reviews = [
        {"customer": "Amanda I.", "rating": 5},
        {"customer": "John D.", "rating": 5},
        {"customer": "Sarah M.", "rating": 5},
        {"customer": "Daniel K.", "rating": 5},
    ]
    return render_template("/dashboard/admin_dashboard.html", salons=salons, reviews=reviews)


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
