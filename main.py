
# # Read settings from env vars (set these on PythonAnywhere)
# DATABRICKS_HOST = "https://dbc-4c3ee4bb-030f.cloud.databricks.com"  # e.g. https://adb-123456789012345.11.azuredatabricks.net
# DATABRICKS_PAT = "dapib38c34617e6cd6ffc69a6f80340e7881"   # your dapib... token


import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Read environment variables (set them in wsgi or PA Web settings)
DATABRICKS_HOST = "https://dbc-4c3ee4bb-030f.cloud.databricks.com"
PAT = "dapib38c34617e6cd6ffc69a6f80340e7881"

@app.route("/")
def root():
    return jsonify({"status": "Flask backend is running"})

@app.route("/approve-model", methods=["GET"])
def approve_model():
    model_name = request.args.get("model_name")
    model_version = request.args.get("model_version")
    run_id = request.args.get("run_id")

    if not model_name or not model_version or not run_id:
        return jsonify({"error": "Missing parameters"}), 400

    jobs_submit_url = f"{DATABRICKS_HOST}/api/2.1/jobs/runs/submit"

    headers = {"Authorization": f"Bearer {PAT}"}

    payload = {
        "run_name": f"approval-{model_name}-v{model_version}",
        "new_cluster": {
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "Standard_DS3_v2",
            "autoscale": {"min_workers": 1, "max_workers": 1}
        },
        "notebook_task": {
            "notebook_path": "/Shared/model_approval_handler",
            "base_parameters": {
                "model_name": model_name,
                "model_version": model_version,
                "run_id": run_id,
                "decision": "APPROVE"
            }
        }
    }

    resp = requests.post(jobs_submit_url, json=payload, headers=headers)

    return jsonify({
        "submitted": True,
        "databricks_status": resp.status_code,
        "response": resp.text
    })
