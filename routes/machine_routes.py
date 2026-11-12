"""
Machine Routes Blueprint
Implements FR-01, FR-02, FR-03, US-01, US-07.
"""
from flask import Blueprint, render_template, abort
from database.connection import get_db
from services.machine_service import get_all_machines, get_machine_by_id
from services.downtime_service import get_downtime_history, get_open_downtime_for_machine

machine_bp = Blueprint("machines", __name__, url_prefix="/machines")

@machine_bp.route("/")
def list_machines():
    db = get_db()
    machines = get_all_machines(db)
    return render_template("machines.html", machines=machines)

@machine_bp.route("/<machine_id>")
def machine_details(machine_id):
    db = get_db()
    machine = get_machine_by_id(db, machine_id)
    if not machine:
        abort(404, description=f"Machine {machine_id} not found.")

    history = get_downtime_history(db, machine_id=machine_id)
    open_event = get_open_downtime_for_machine(db, machine_id)

    return render_template("machine_details.html", machine=machine, history=history, open_event=open_event)
