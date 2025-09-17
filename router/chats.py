# routes/chat_logger.py
from flask import Blueprint, jsonify
import json, os

chat_logger_bp = Blueprint("chat_logger", __name__)
LOG_FILE = "chat_logs.json"


def read_logs():
    """Read chat logs from the JSON file."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@chat_logger_bp.route("/api/chats", methods=["GET"])
def get_chats():
    """Return saved chat logs (read-only)."""
    return jsonify(read_logs())
