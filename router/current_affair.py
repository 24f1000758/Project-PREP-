import os
import json
from flask import request, jsonify, Blueprint, current_app

# =====================================================
# 🔹 CURRENT AFFAIRS API ROUTE
# =====================================================
current_bp = Blueprint('current_bp', __name__, url_prefix='/api')

@current_bp.route("/current_affairs", methods=["GET"])
def get_current_affairs():
    """
    Fetches current affairs from a local JSON file (news.json).
    Filters by domain and time period if provided.
    """
    try:
        # Path to the local news.json file
        news_file = os.path.join(current_app.root_path, "news.json")

        if not os.path.exists(news_file):
            return jsonify({"error": "news.json file not found on server."}), 500

        with open(news_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract filters from query params
        domain = request.args.get("domain", "").lower()
        time_period = request.args.get("time_period", "").lower()

        # --- Filter by domain (if provided)
        if domain:
            data = [item for item in data if item.get("domain", "").lower().startswith(domain)]

        # --- (Optional) Filter by time_period (today, this-week, this-month)
        # Since the JSON file contains dates in "September 5, 2025" format,
        # you can implement logic to filter here if needed.
        # For now, returning all.

        # Add unique IDs for frontend
        for idx, article in enumerate(data):
            article["id"] = idx

        return jsonify({"current_affairs": data}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in news.json."}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected server error occurred."}), 500





# Generate current affairs news updates suitable for government exam preparation (UPSC, SSC, Banking, State PCS). The news should cover key domains:

# Economy & Policy

# Polity & Governance

# International Relations

# Defence & Security

# Environment & Ecology

# Science & Technology

# Reports, Indices & Rankings

# Awards & Personalities

# Government Schemes & Initiatives

# Guidelines:

# Write in a concise, factual, exam-focused style.

# Highlight data points, names, reports, schemes, acts, locations, and dates that may be asked in MCQs or descriptive exams.

# Avoid opinion or unnecessary storytelling.

# Add a short explanation for context, but keep it exam-oriented.

# Each news item should be 2–4 lines long.

# Format Output as JSON array:
# [

#   {
#     "domain": "Economy & Policy",
#     "headline": "India's GST Council announces major tax rate overhaul",
#     "explain": "The GST Council merged multiple slabs into 5% and 18% categories, and introduced a 40% levy on luxury goods. Effective from Sep 22, 2025. Aim: boost consumption and simplify compliance."
#     "date": "date of news"
#   },
#   {
#     "domain": "International Relations",
#     "headline": "India joins IEA critical minerals partnership",
#     "explain": "India became a member of the International Energy Agency's Critical Minerals Security Partnership (CMSP), enhancing supply-chain resilience for lithium, cobalt, and nickel."
#     "date": "date of news"
#   }
# ]