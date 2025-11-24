from flask import Flask, request, jsonify
import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# ------------------------------------------------------
# GOOGLE SHEETS API AUTHENTICATION (Render-Safe)
# ------------------------------------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load service account JSON from environment variable
service_json = os.environ.get("SERVICE_ACCOUNT_JSON")

if not service_json:
    raise Exception("SERVICE_ACCOUNT_JSON not found. Add it in Render → Environment.")

# Write the JSON to a file Render can access
with open("service_account.json", "w") as f:
    f.write(service_json)

# Authenticate
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json", SCOPE
)
client = gspread.authorize(creds)

# Your sheet ID
SHEET_ID = "17B_nr58UEikILpOip9Bzy87z8IQrF0H_2XA7qXzlNlE"
sheet = client.open_by_key(SHEET_ID).sheet1


# ------------------------------------------------------
# APPROVAL ENDPOINT
# ------------------------------------------------------
@app.get("/approve")
def approve():
    try:
        run_id = request.args.get("run_id")
        model_name = request.args.get("model_name")
        model_version = request.args.get("model_version")

        if not run_id:
            return jsonify({"error": "Missing run_id"}), 400

        # Append to Google Sheet
        sheet.append_row([run_id, model_name, model_version, "TRUE"])

        return jsonify({
            "status": "SUCCESS",
            "message": "Approval recorded successfully.",
            "run_id": run_id,
            "model_name": model_name,
            "model_version": model_version
        })

    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500


# ------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------
@app.get("/")
def home():
    return "Databricks Approval Backend is running!"


# ------------------------------------------------------
# RUN FLASK (ignored by Render, but useful locally)
# ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
