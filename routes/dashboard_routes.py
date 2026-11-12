"""
Dashboard Blueprint
Implements FR-02, FR-03, FR-11, US-01, US-05, US-10.
"""
from flask import Blueprint, render_template
from database.connection import get_db
from services.downtime_service import get_dashboard_metrics
from services.machine_service import get_all_machines

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    db = get_db()
    metrics = get_dashboard_metrics(db)
    machines = get_all_machines(db)
    return render_template("dashboard.html", metrics=metrics, machines=machines)
