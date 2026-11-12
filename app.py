import os
import logging
from flask import Flask, render_template
from config import Config, get_config
from database.connection import close_db, get_db
from database.init_db import init_db
from services.cost_service import format_currency_inr, format_duration

def create_app(config_class=None):
    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure Application Logging
    if not app.logger.handlers:
        logging.basicConfig(
            level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    # Register teardown
    app.teardown_appcontext(close_db)

    # Register custom template filters
    @app.template_filter("currency_inr")
    def currency_filter(val):
        return format_currency_inr(val)

    @app.template_filter("duration_fmt")
    def duration_filter(val):
        return format_duration(val)

    # Ensure database directory and file exist on startup (except for in-memory test databases)
    if not app.config.get("TESTING") and app.config["DATABASE_PATH"] != ":memory:":
        db_dir = os.path.dirname(app.config["DATABASE_PATH"])
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            app.logger.info(f"Created persistent database directory at: {db_dir}")

        if not os.path.exists(app.config["DATABASE_PATH"]):
            app.logger.info(f"Initializing new SQLite database at: {app.config['DATABASE_PATH']}")
            init_db(app.config["DATABASE_PATH"], populate_sample_data=True)
        else:
            app.logger.info(f"Connecting to existing persistent database at: {app.config['DATABASE_PATH']}")

    # Register Blueprints
    from routes.dashboard_routes import dashboard_bp
    from routes.machine_routes import machine_bp
    from routes.downtime_routes import downtime_bp
    from routes.work_order_routes import work_order_bp
    from routes.report_routes import report_bp
    from routes.simulator_routes import simulator_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(machine_bp)
    app.register_blueprint(downtime_bp)
    app.register_blueprint(work_order_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(simulator_bp)

    # Health Check & Monitoring Endpoint
    @app.route("/health")
    def health_check():
        """Lightweight monitoring and health check endpoint."""
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = "healthy"
        except Exception as e:
            app.logger.error(f"Health check DB probe failed: {e}")
            db_status = f"unhealthy: {str(e)}"

        status_code = 200 if db_status == "healthy" else 503
        return {
            "status": "UP" if status_code == 200 else "DEGRADED",
            "service": "Factory Shop-Floor Execution System - Downtime Logger",
            "database": db_status
        }, status_code

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_message="404 - Resource Not Found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("base.html", error_message="500 - Internal Server Error"), 500

    return app

if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    debug = app.config.get("DEBUG", False)

    app.logger.info(f"Starting Factory Shop-Floor System on http://{host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)
