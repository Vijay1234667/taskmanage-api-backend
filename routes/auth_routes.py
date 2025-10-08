from flask import Blueprint, request, jsonify
import hashlib, jwt
from db import get_db_connection
from config import Config
from datetime import datetime, timedelta

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email.endswith("@mobavenue.com"):
        return jsonify({"success": False, "message": "Only Mobavenue emails are permitted."}), 400

    hashed_password = hashlib.md5(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"}), 400

    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                   (name, email, hashed_password, "employee"))
    conn.commit()
    user_id = cursor.lastrowid

    cursor.execute("INSERT INTO assignees (name, user_id) VALUES (%s, %s)", (name, user_id))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "User registered and assignee added"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role FROM users WHERE email = %s AND password = %s",(email, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    payload = {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRES_IN)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return jsonify({"success": True, "user": user, "token": token})