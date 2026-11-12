"""
Simulator API & UI Blueprint
Implements FR-15, FR-16, FR-20, FR-21, FR-22, FR-23, US-08.
"""
from flask import Blueprint, request, jsonify, render_template
from database.connection import get_db
from services.validation_service import validate_simulator_payload
from services.downtime_service import start_downtime, resume_downtime
from services.machine_service import get_all_machines

simulator_bp = Blueprint("simulator", __name__)

@simulator_bp.route("/simulator")
def simulator_ui():
    """Interactive web console for student simulation testing."""
    db = get_db()
    machines = get_all_machines(db)
    return render_template("simulator.html", machines=machines)

@simulator_bp.route("/api/simulator/events", methods=["POST"])
def receive_event():
    """
    POST /api/simulator/events
    Accepts JSON payloads for STOP and RESUME machine events.
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Invalid request content-type. Expected application/json."
        }), 400

    data = request.get_json()
    is_valid, error_msg, parsed = validate_simulator_payload(data)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 400

    db = get_db()
    event_type = parsed["event_type"]
    machine_id = parsed["machine_id"]
    timestamp = parsed["timestamp"]
    source = parsed["source"]
    event_id = parsed["event_id"]

    try:
        if event_type == "STOP":
            downtime_id = start_downtime(
                db=db,
                machine_id=machine_id,
                reason=parsed["reason"],
                start_time=timestamp,
                work_order_id=parsed["work_order_id"],
                source=source,
                event_id=event_id
            )
            return jsonify({
                "status": "success",
                "message": f"Downtime event #{downtime_id} successfully created for machine {machine_id}.",
                "data": {
                    "downtime_id": downtime_id,
                    "machine_id": machine_id,
                    "event_status": "OPEN",
                    "machine_status": "DOWN",
                    "timestamp": timestamp.isoformat(),
                    "source": source
                }
            }), 201

        elif event_type == "RESUME":
            res = resume_downtime(
                db=db,
                machine_id=machine_id,
                end_time=timestamp,
                source=source,
                event_id=event_id
            )
            return jsonify({
                "status": "success",
                "message": f"Machine {machine_id} resumed and downtime #{res['downtime_id']} closed.",
                "data": {
                    "downtime_id": res["downtime_id"],
                    "machine_id": machine_id,
                    "event_status": "CLOSED",
                    "machine_status": "RUNNING",
                    "duration_seconds": res["duration_seconds"],
                    "estimated_cost": res["estimated_cost"],
                    "start_time": res["start_time"],
                    "end_time": res["end_time"],
                    "source": source
                }
            }), 200

    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server processing error: {str(e)}"
        }), 500
