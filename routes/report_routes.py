"""
Report Blueprint
Implements FR-10, FR-11, FR-24, US-05, US-10.
"""
from flask import Blueprint, render_template, request
from database.connection import get_db
from services.downtime_service import get_reports_summary

report_bp = Blueprint("reports", __name__, url_prefix="/reports")

@report_bp.route("/")
def index():
    db = get_db()
    start_date = request.args.get("start_date", "").strip() or None
    end_date = request.args.get("end_date", "").strip() or None

    summary = get_reports_summary(db, start_date=start_date, end_date=end_date)
    return render_template(
        "reports.html",
        summary=summary,
        start_date=start_date or "",
        end_date=end_date or ""
    )
