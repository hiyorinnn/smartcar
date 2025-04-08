from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
import datetime
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database Configuration (Using Flask-SQLAlchemy)
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "host.docker.internal")  # Works with Docker
DB_NAME = os.environ.get("DB_NAME", "smartcar_logs")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}

db = SQLAlchemy(app)

# Logging Configuration
LOG_DIR = "/app/logs" if os.getenv("DOCKER_ENV") else "C:/wamp64/www/smartcar/microservices/error-handling-service/logs"
LOG_FILE = os.path.join(LOG_DIR, "error_log.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()  # Log to console
    ]
)

# Add Flask error logging
flask_handler = logging.FileHandler(LOG_FILE)
flask_handler.setLevel(logging.ERROR)
flask_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


# Define error log table
class ErrorLog(db.Model):
    __tablename__ = "error_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.String(10), nullable=False)
    client_ip = db.Column(db.String(45), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, level, client_ip, method, url, status_code, message):
        self.level = level
        self.client_ip = client_ip
        self.method = method
        self.url = url
        self.status_code = status_code
        self.message = message

@app.route("/")
def home():
    return jsonify({"message": "Error Handler Service is Running"}), 200


# Log errors to database
def log_to_database(level, client_ip, method, url, status_code, message):
    """Logs error details to the MySQL database."""
    try:
        error_log = ErrorLog(level, client_ip, method, url, status_code, message)
        db.session.add(error_log)
        db.session.commit()  # Commit to ensure data is saved
        print(f"Logged to DB: {message}")  # Add this line for debugging
    except Exception as e:
        # Log database connection error to file if any issue arises
        app.logger.error(f"Database Error: {e}")
        db.session.rollback()  # Rollback to maintain integrity
        db.session.remove()  # Ensure session is properly closed
        print(f"DB Error: {e}")  # Debugging


# Error Handling
@app.errorhandler(404)
def not_found(error):
    return handle_error(404, "Not Found", str(error))


@app.errorhandler(500)
def internal_server_error(error):
    return handle_error(500, "Internal Server Error", str(error))


@app.errorhandler(400)
def bad_request(error):
    return handle_error(400, "Bad Request", str(error))


@app.errorhandler(Exception)
def handle_exception(e):
    return handle_error(500, "Internal Server Error", str(e))


def handle_error(status_code, error_type, message):
    """Handles errors by logging them and returning a JSON response."""
    client_ip = request.remote_addr if hasattr(request, "remote_addr") else "Unknown IP"
    method = request.method if hasattr(request, "method") else "UNKNOWN"
    url = request.path if hasattr(request, "path") else "UNKNOWN"


    # Log the error details to the console and file
    app.logger.error(f"[{client_ip}] {method} {url} - {status_code} {error_type}: {message}")
    logging.error(f"[{client_ip}] {method} {url} - {status_code} {error_type}: {message}")

    # Log to MySQL
    log_to_database("ERROR", client_ip, method, url, status_code, message)

    return jsonify({
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status": status_code,
        "error": error_type,
        "message": message,
    }), status_code

@app.route("/api/log-error", methods=["POST"])
def log_external_error():
    """Receives error details from external microservices and logs them."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    status_code = data.get("status_code", 500)
    error_type = data.get("error_type", "Unknown Error")
    message = data.get("message", "No details provided")

    return handle_error(status_code, error_type, message)

@app.route("/test-db-log", methods=["GET"])
def test_db_log():
    try:
        log_to_database("ERROR", "127.0.0.1", "GET", "/test-db-log", 500, "Test error log entry")
        return jsonify({"message": "Database log entry added"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True, host="0.0.0.0", port=5005)

