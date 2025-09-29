# pip install -r requirements.txt


from flask import Flask, request, redirect, jsonify
import requests
import os

from browser_automation import open_browser_and_press_key

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1422219887236878528/P6E0gIekXIsa5safVEZEHsqpbAFTpI_IdsJFI0rzscXIsiTqepwe3iMzYWJ5cOsIX6Ti"

app = Flask(__name__)

import os
import requests

import os
import requests
# Assume DISCORD_WEBHOOK_URL is defined somewhere globally

import os
import requests
import os
import json
import requests


def testDiscord():
    # Extracted signal data from the image
    signal_title = "BTCUSDT.P – Bärische Divergenz (Bearish Divergence)"
    signal_message = (
        "Eine bärische Divergenz ist kein garantierter Trendwechsel, "
        "sondern ein Hinweis auf eine mögliche Abschwächung des Aufwärtstrends "
        "— Bestätigung durch Preisaction oder Volumenanalyse ist ratsam."
    )
    exchange = "BINGX"
    timeframe = "15"
    price = "112041.8"

    # Define the payload with two embeds: one for text, one for the image
    payload = {
        "embeds": [
            {
                "title": signal_title,
                "fields": [
                    {
                        "name": "Analysis",
                        "value": signal_message
                    },
                    {
                        "name": "Exchange",
                        "value": exchange,
                        "inline": True
                    },
                    {
                        "name": "Timeframe",
                        "value": f"{timeframe} minutes",
                        "inline": True
                    },
                    {
                        "name": "Price",
                        "value": price,
                        "inline": True
                    }
                ],
                "color": 0xFF0000  # Optional: Red color for the embed
            },
            {
                "image": {
                    "url": "attachment://BTCUSD_2025-09-29_16-05-29.png"  # Reference the attached image
                }
            }
        ]
    }

    # File path for the image
    file_path = "downloads\\BTCUSD_2025-09-29_16-05-29.png"
    
    # Send the request
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'image/png')}
        data = {
            "payload_json": json.dumps(payload)  # Serialize payload to a JSON string
        }
        
        try:
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

# testDiscord()

def send_to_discord(file_path, symbol):
    """
    Sends a chart screenshot and related signal information to a Discord webhook,
    using embeds with inline fields.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Error: Screenshot file not found at {file_path}")
        return

    # Extracted signal data from the image
    signal_title = "BTCUSDT.P – Bärische Divergenz (Bearish Divergence)"
    signal_message = (
        "Eine bärische Divergenz ist kein garantierter Trendwechsel, "
        "sondern ein Hinweis auf eine mögliche Abschwächung des Aufwärtstrends "
        "— Bestätigung durch Preisaction oder Volumenanalyse ist ratsam."
    )
    exchange = "BINGX"
    timeframe = "15"
    price = "112041.8"

    # Construct the embed payload
    payload = {
        "embeds": [
            {
                "title": signal_title,
                "fields": [
                    {
                        "name": "Exchange",
                        "value": exchange,
                        "inline": True
                    },
                    {
                        "name": "Timeframe",
                        "value": f"{timeframe} minutes",
                        "inline": True
                    },
                    {
                        "name": "Price",
                        "value": price,
                        "inline": True
                    },
                    {
                        "name": "Analysis",
                        "value": signal_message
                    }
                ]
            }
        ]
    }

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/png')}
            
            response = requests.post(
                DISCORD_WEBHOOK_URL, 
                json=payload,
                files=files
            )
            
            response.raise_for_status()
            print(f"Discord message sent successfully. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        
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

@app.route('/<string:webhook_id>', methods=['POST'])
def handle_chart_webhook(webhook_id):
    data = request.get_json()
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Missing 'symbol' in request body"}), 400

    symbol = data['symbol']
    print(f"Received webhook for ID '{webhook_id}' with symbol: {symbol}")

    chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

    try:
        from selenium.webdriver.common.keys import Keys
        screenshot_path = open_browser_and_press_key(chart_url, Keys.CONTROL, Keys.ALT, 's')

        if screenshot_path:
            print(f"Screenshot saved to: {screenshot_path}")
            # forward_to_make_webhook(webhook_id, data)
            send_to_discord(screenshot_path, symbol)
            os.remove(screenshot_path)
            return jsonify({"status": "success", "message": f"Screenshot for {symbol} sent to Discord."})
        else:
            return jsonify({"status": "error", "message": "Failed to download screenshot."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
