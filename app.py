from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

def get_access_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    return response.json().get("access_token")

@app.route("/add-event", methods=["POST"])
def add_event():
    req_data = request.json
    if req_data.get("token") != ACCESS_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 500

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    event_data = {
        "summary": req_data.get("summary"),
        "description": req_data.get("description", ""),
        "start": {
            "dateTime": req_data.get("start"),
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": req_data.get("end"),
            "timeZone": "America/New_York"
        }
    }

    response = requests.post(GOOGLE_CALENDAR_API, headers=headers, json=event_data)

    if response.status_code != 200:
        return jsonify({"error": "Failed to create event", "details": response.text}), 500

    return jsonify({"status": "Event created", "data": response.json()})

@app.route("/")
def index():
    return "Ema is live, secure, and calendar-connected. 💋"

if __name__ == "__main__":
    app.run(debug=True)
