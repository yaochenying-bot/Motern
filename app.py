from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import date
from urllib.parse import quote_plus

import requests
from flask import Flask, jsonify, request, send_from_directory

from alert_logic import developers_without_plan, load_schedules

app = Flask(__name__, static_folder="web", static_url_path="")


def _build_dingtalk_signed_url(webhook: str, secret: str) -> str:
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    hmac_code = hmac.new(secret.encode("utf-8"), string_to_sign, digestmod=hashlib.sha256).digest()
    sign = quote_plus(base64.b64encode(hmac_code))
    delimiter = "&" if "?" in webhook else "?"
    return f"{webhook}{delimiter}timestamp={timestamp}&sign={sign}"


def _fetch_tapd_calendar(tapd_calendar_api: str, tapd_token: str | None) -> dict:
    headers = {}
    if tapd_token:
        headers["Authorization"] = f"Bearer {tapd_token}"
    response = requests.get(tapd_calendar_api, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def _send_dingtalk_alert(webhook: str, secret: str | None, message: str) -> dict:
    target = _build_dingtalk_signed_url(webhook, secret) if secret else webhook
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "开发排期告警",
            "text": message,
        },
    }
    response = requests.post(target, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=20)
    response.raise_for_status()
    return response.json()


@app.get("/")
def index():
    return send_from_directory("web", "index.html")


@app.post("/api/check-alerts")
def check_alerts():
    body = request.get_json(force=True)
    tapd_calendar_api = body.get("tapd_calendar_api")
    dingtalk_webhook = body.get("dingtalk_webhook")
    if not tapd_calendar_api or not dingtalk_webhook:
        return jsonify({"error": "tapd_calendar_api 和 dingtalk_webhook 不能为空"}), 400

    tapd_token = body.get("tapd_token")
    dingtalk_secret = body.get("dingtalk_secret")
    now = date.today()

    tapd_payload = _fetch_tapd_calendar(tapd_calendar_api, tapd_token)
    schedules = load_schedules(tapd_payload)
    idle_devs = developers_without_plan(schedules, now=now, within_days=2)

    if idle_devs:
        dev_lines = "\n".join(f"- {name}" for name in idle_devs)
        text = f"### 开发排期告警\n以下开发同学在未来 2 天内没有工作安排，请及时补充排期：\n{dev_lines}"
        dingtalk_resp = _send_dingtalk_alert(dingtalk_webhook, dingtalk_secret, text)
        return jsonify({"alerted": True, "idle_developers": idle_devs, "dingtalk_response": dingtalk_resp})

    return jsonify({"alerted": False, "idle_developers": []})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
