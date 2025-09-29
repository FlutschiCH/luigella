from flask import Flask, request, jsonify
import requests
import os
import json
import traceback
from selenium.webdriver.common.keys import Keys

from browser_automation import open_browser_and_press_key

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1422219887236878528/P6E0gIekXIsa5safVEZEHsqpbAFTpI_IdsJFI0rzscXIsiTqepwe3iMzYWJ5cOsIX6Ti"

app = Flask(__name__)

def send_to_discord(file_path, webhook_data):
    """
    Sends a chart screenshot and related signal information to a Discord webhook,
    using embeds with inline fields.
    """
    symbol = webhook_data.get("symbol", "N/A")
    divergence = webhook_data.get("divergenz", "N/A").capitalize()
    exchange = webhook_data.get("exchange", "N/A")
    timeframe = webhook_data.get("timeframe", "N/A")
    price = webhook_data.get("price", "N/A")

    payload = {
        "embeds": [
            {
                "title": f"{symbol} – {divergence} Divergence",
                "fields": [
                    {
                        "name": "Exchange",
                        "value": exchange,
                        "inline": True
                    },
                    {
                        "name": "Timeframe",
                        "value": f"{timeframe}m",
                        "inline": True
                    },
                    {
                        "name": "Price",
                        "value": str(price),
                        "inline": True
                    }
                ],
                "color": 0xFF0000 if "bearish" in divergence.lower() else 0x00FF00
            },
            {
                "image": {
                    "url": f"attachment://{os.path.basename(file_path)}"  # Reference the attached image
                }
            }
        ]
    }

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/png')}
            data = {"payload_json": json.dumps(payload)}
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data=data,
                files=files
            )
            response.raise_for_status()
            print(f"Discord message sent successfully. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")

def forward_to_make_webhook(webhook_id, data):
    make_url = f"https://hook.eu2.make.com/{webhook_id}"
    try:
        print(f"Forwarding data to Make.com webhook: {make_url}")
        response = requests.post(make_url, json=data, timeout=10)
        print(f"Make.com response: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error forwarding webhook to Make.com: {e}")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/', methods=['POST'])
def handle_chart_webhook():
    data = request.get_json()
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Missing 'symbol' in request body"}), 400

    symbol = data['symbol']
    print(f"Received webhook with symbol: {symbol}")

    chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

    try:
        screenshot_path = open_browser_and_press_key(chart_url, Keys.CONTROL, Keys.ALT, 's')

        if screenshot_path:
            print(f"Screenshot saved to: {screenshot_path}")
            # forward_to_make_webhook(webhook_id, data)
            send_to_discord(screenshot_path, data)
            os.remove(screenshot_path)
            return jsonify({"status": "success", "message": f"Screenshot for {symbol} sent to Discord."})
        else:
            return jsonify({"status": "error", "message": "Failed to download screenshot."}), 500

    except Exception as e:
        tb_str = traceback.format_exc()
        error_message = f"An unexpected error occurred: {e}"
        print(f"ERROR: {error_message}\n{tb_str}")
        return jsonify({
            "status": "error",
            "message": error_message,
            "details": tb_str
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
