from flask import Blueprint, jsonify, request
from db import get_db_connection
from middleware.auth import authenticate_token
from config import Config

assignee_bp = Blueprint("assignee_bp", __name__)

@assignee_bp.route("", methods=["GET"])
@assignee_bp.route("/", methods=["GET"])
@authenticate_token
def get_assignees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assignees")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


@assignee_bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@authenticate_token
def delete_assignee(id):
    if request.method == "OPTIONS":
        return "", 200 

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignees WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Deleted"})