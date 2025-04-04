from flask import Flask, send_from_directory, jsonify, request
from config import LOG_FILE_PATH, LOG_LEVEL
import os
import logging
import datetime

# Set the correct static folder path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "my-vue-project", "dist"))

app = Flask(__name__, static_folder=STATIC_DIR)

# Configure Logging
logging.basicConfig(
    filename="logs/error_log.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Serve the Vue index.html at root "/"
@app.route("/")
def serve_vue():
    return send_from_directory(STATIC_DIR, "index.html")

# Serve static files (JS, CSS, images)
@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory(os.path.join(STATIC_DIR, "assets"), path)

# Catch-all route to handle Vue Router history mode
@app.route("/<path:path>")
def catch_all(path):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")  #Serve index.html for Vue Router

# Custom Error Handling
@app.errorhandler(400)
def bad_request(error):
    return handle_error(400, "Bad Request", str(error))

@app.errorhandler(404)
def not_found(error):
    return handle_error(404, "Not Found", str(error))

@app.errorhandler(500)
def internal_error(error):
    return handle_error(500, "Internal Server Error", str(error))

def handle_error(status_code, error_type, message):
    error_response = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status": status_code,
        "error": error_type,
        "message": message,
    }
    logging.error(f"{status_code} - {error_type}: {message}")
    return jsonify(error_response), status_code

# Start Flask server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)
