from flask import Blueprint, request, jsonify
from db import get_db_connection
from middleware.auth import authenticate_token

task_bp = Blueprint('task_bp', __name__)

@task_bp.route("", methods=["GET"])
@authenticate_token
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@task_bp.route("", methods=["POST"])
@authenticate_token
def create_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    project = data.get("project")
    assignee = data.get("assignee")
    priority = data.get("priority")
    status = data.get("status")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM assignees WHERE id=%s", (assignee,))
    if not cursor.fetchone():
        return jsonify({"message": "Invalid assignee ID"}), 400

    cursor.execute("SELECT id FROM projects WHERE id=%s", (project,))
    if not cursor.fetchone():
        return jsonify({"message": "Invalid project ID"}), 400

    cursor.execute(
        "INSERT INTO tasks (title, description, project, assignee, priority, status, start_date, end_date) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (title, description, project, assignee, priority, status, start_date, end_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Task created", "taskId": task_id}), 201

@task_bp.route("/<int:id>", methods=["PUT"])
@authenticate_token
def update_task(id):
    data = request.get_json()
    print("Received JSON:", data)
    if not data:
        return jsonify({"message": "No JSON received"}), 400

    required_fields = ["title","description","project","assignee","priority","status","start_date","end_date"]
    missing_fields = [f for f in required_fields if not data.get(f)]
    if missing_fields:
        print("Missing fields:", missing_fields)
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    title = data["title"]
    description = data["description"]
    project = data["project"]
    assignee = data["assignee"]
    priority = data["priority"]
    status = data["status"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM assignees WHERE id=%s", (assignee,))
    if not cursor.fetchone():
        return jsonify({"message": "Invalid assignee ID"}), 400

    cursor.execute("SELECT id FROM projects WHERE id=%s", (project,))
    if not cursor.fetchone():
        return jsonify({"message": "Invalid project ID"}), 400

    cursor.execute(
        "UPDATE tasks SET title=%s, description=%s, project=%s, assignee=%s, priority=%s, status=%s, start_date=%s, end_date=%s"
        "WHERE id=%s",
        (title, description, project, assignee, priority, status, start_date, end_date, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Task updated"})

@task_bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@authenticate_token
def delete_task(id):
    if request.method == "OPTIONS":
        return '', 200

    # username & role
    data = request.get_json() or {}
    username = data.get("username") or request.args.get("username")
    role = data.get("role") or request.args.get("role")

    print("Incoming DELETE request for task ID:", id)
    print("Username:", username, "Role:", role)
    print("Headers:", dict(request.headers))
    print("Full request args:", request.args)
    print("Request JSON:", data)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    task = cursor.fetchone()
    print("Fetched task:", task)

    if not task:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Task not found"}), 404

    if role == "manager" or str(task["assignee"]) == username:
        cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Task deleted successfully"})
    else:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Not allowed"}), 403