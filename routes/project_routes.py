from flask import Blueprint, request, jsonify
from db import get_db_connection
from middleware.auth import authenticate_token

project_bp = Blueprint('project_bp', __name__)

@project_bp.route("", methods=["GET"])
@authenticate_token
def get_projects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@project_bp.route("", methods=["POST"])
@authenticate_token
def create_project():
    data = request.get_json()
    name, description = data.get("name"), data.get("description")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, description) VALUES (%s, %s)", (name, description))
    conn.commit()
    project_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": project_id, "name": name, "description": description}), 201

@project_bp.route("/<int:id>", methods=["PUT"])
@authenticate_token
def update_project(id):
    data = request.get_json()
    name, description = data.get("name"), data.get("description")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET name=%s, description=%s WHERE id=%s", (name, description, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": id, "name": name, "description": description})

@project_bp.route("/<int:id>", methods=["DELETE"])
@authenticate_token
def delete_project(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Deleted"})
