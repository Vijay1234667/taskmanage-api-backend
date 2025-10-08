from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def authenticate_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200  # allow preflight
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"message": "Missing token"}), 401
        # decode and verify token
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper
