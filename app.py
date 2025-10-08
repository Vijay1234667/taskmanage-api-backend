from flask import Flask
from flask_cors import CORS
import os

from routes.auth_routes import auth_bp
from routes.assignee_routes import assignee_bp
from routes.project_routes import project_bp
from routes.task_routes import task_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"],methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

app.register_blueprint(auth_bp)
app.register_blueprint(assignee_bp, url_prefix="/assignees", strict_slashes=False)
app.register_blueprint(project_bp, url_prefix="/projects",strict_slashes=False)
app.register_blueprint(task_bp, url_prefix="/tasks", strict_slashes=False)

@app.route("/")
def home():
    return "Mobavenue Task Management API is running."

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render ka port variable use kare
    app.run(host="0.0.0.0", port=port, debug=True)