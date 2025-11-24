from flask import Flask, request, jsonify
import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- Load service account from environment variable ---
service_json = os.environ.get("SERVICE_ACCOUNT_JSON")

if not service_json:
    raise Exception("SERVICE_ACCOUNT_JSON env variable not found in Render!")

# write JSON to local file
with open("service_account.json", "w") as f:
    f.write(service_json)

# authenticate
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
client = gspread.authorize(creds)

SHEET_ID = "17B_nr58UEikILpOip9Bzy87z8IQrF0H_2XA7qXzlNlE"
sheet = client.open_by_key(SHEET_ID).sheet1


@app.route("/")
def home():
    return "Approval Backend Running"


@app.route("/approve", methods=["GET"])
def approve():
    run_id = request.args.get("run_id")
    model_name = request.args.get("model_name")
    model_version = request.args.get("model_version")

    sheet.append_row([run_id, model_name, model_version, "APPROVED"])

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run()
