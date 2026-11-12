"""
Work Order Blueprint
Implements FR-17, US-06.
"""
from flask import Blueprint, render_template
from database.connection import get_db
from services.work_order_service import get_all_work_orders

work_order_bp = Blueprint("work_orders", __name__, url_prefix="/work-orders")

@work_order_bp.route("/")
def list_work_orders():
    db = get_db()
    work_orders = get_all_work_orders(db)
    return render_template("work_orders.html", work_orders=work_orders)
