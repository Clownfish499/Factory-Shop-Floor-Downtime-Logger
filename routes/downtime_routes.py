"""
Downtime Routes Blueprint
Implements FR-04, FR-05, FR-06, FR-07, FR-08, FR-12, FR-14, US-02, US-03, US-04, US-06, US-09.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connection import get_db
from services.machine_service import get_all_machines
from services.work_order_service import get_all_work_orders
from services.downtime_service import start_downtime, resume_downtime, get_downtime_history
from services.validation_service import validate_reason

downtime_bp = Blueprint("downtime", __name__, url_prefix="/downtime")

@downtime_bp.route("/history")
def history():
    db = get_db()
    machine_id = request.args.get("machine_id", "").strip() or None
    status = request.args.get("status", "").strip() or None
    start_date = request.args.get("start_date", "").strip() or None
    end_date = request.args.get("end_date", "").strip() or None

    logs = get_downtime_history(db, machine_id=machine_id, status=status, start_date=start_date, end_date=end_date)
    machines = get_all_machines(db)

    return render_template(
        "downtime_history.html",
        logs=logs,
        machines=machines,
        selected_machine=machine_id or "",
        selected_status=status or "",
        start_date=start_date or "",
        end_date=end_date or ""
    )

@downtime_bp.route("/start", methods=["GET", "POST"])
def start():
    db = get_db()
    machines = get_all_machines(db)
    work_orders = get_all_work_orders(db)

    preselected_machine = request.args.get("machine_id", "")

    if request.method == "POST":
        machine_id = request.form.get("machine_id", "").strip()
        reason = request.form.get("reason", "").strip()
        work_order_id = request.form.get("work_order_id", "").strip() or None
        custom_timestamp = request.form.get("timestamp", "").strip()

        # Validation
        if not machine_id:
            flash("Please select a machine.", "danger")
            return render_template("downtime_form.html", machines=machines, work_orders=work_orders, preselected=machine_id)

        valid_r, err_r = validate_reason(reason)
        if not valid_r:
            flash(err_r, "danger")
            return render_template("downtime_form.html", machines=machines, work_orders=work_orders, preselected=machine_id, reason=reason)

        try:
            start_time = custom_timestamp if custom_timestamp else None
            dt_id = start_downtime(
                db=db,
                machine_id=machine_id,
                reason=reason,
                start_time=start_time,
                work_order_id=work_order_id,
                source="MANUAL"
            )
            flash(f"Downtime event #{dt_id} started successfully for Machine {machine_id}.", "success")
            return redirect(url_for("downtime.history"))
        except Exception as e:
            flash(str(e), "danger")
            return render_template("downtime_form.html", machines=machines, work_orders=work_orders, preselected=machine_id, reason=reason)

    return render_template("downtime_form.html", machines=machines, work_orders=work_orders, preselected=preselected_machine)

@downtime_bp.route("/resume/<machine_id>", methods=["POST"])
def resume(machine_id):
    db = get_db()
    try:
        res = resume_downtime(db, machine_id=machine_id, source="MANUAL")
        flash(f"Machine {machine_id} resumed successfully! Elapsed downtime: {res['duration_seconds']} seconds ({res['duration_seconds']//60} mins). Estimated Cost: Rs. {res['estimated_cost']:,.2f}", "success")
    except Exception as e:
        flash(f"Failed to resume machine {machine_id}: {str(e)}", "danger")

    next_url = request.referrer or url_for("dashboard.index")
    return redirect(next_url)
