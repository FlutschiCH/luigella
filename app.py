from flask import Flask, request, jsonify
import requests
import os
import json
import traceback
import queue
import threading
from selenium.webdriver.common.keys import Keys

from browser_automation import open_browser_and_press_key

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1422219887236878528/P6E0gIekXIsa5safVEZEHsqpbAFTpI_IdsJFI0rzscXIsiTqepwe3iMzYWJ5cOsIX6Ti"

app = Flask(__name__)

# Create a queue to hold incoming webhook tasks
task_queue = queue.Queue()

def _send_debug_to_discord(webhook_data):
    """Sends the raw webhook JSON to the default Discord channel for debugging."""
    try:
        # Format the JSON data for readability in Discord
        pretty_json = json.dumps(webhook_data, indent=2)
        message = f"```json\n{pretty_json}\n```"
        
        payload = {
            "content": "Received new signal payload:",
            "embeds": [{
                "description": message,
                "color": 8421504 # Grey color
            }]
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send debug message to Discord: {e}")

def send_to_discord(file_path, webhook_data):
    """
    Sends a chart screenshot and related signal information to a Discord webhook,
    using embeds with inline fields.
    """
    symbol = webhook_data.get("symbol", "N/A")
    divergence = webhook_data.get("divergenz", "N/A").capitalize()

    # Send the raw JSON to the debug channel first
    _send_debug_to_discord(webhook_data)
    exchange = webhook_data.get("exchange", "N/A")
    timeframe = webhook_data.get("timeframe", "N/A")
    price = webhook_data.get("price", "N/A")
    time = webhook_data.get("timenow", "N/A")
    description = webhook_data.get("description", "")
    title = webhook_data.get("title", f"{symbol} Signal")
    color = webhook_data.get("color", "000")
    discordLink = webhook_data.get("discordLink", "")

    if timeframe == "S":
        timeframe = "1S"

    # If the discordLink is empty, send an error to the default webhook.
    if discordLink == "":
        print("ERROR: 'discordLink' was not provided in the webhook data. Sending notification to default channel.")
        error_payload = {
            "embeds": [{
                "title": "Webhook Configuration Error",
                "description": f"Received a signal for **{symbol}** but the `discordLink` was missing in the webhook payload.",
                "color": 15158332, # Red color
                "timestamp": time,
                "footer": { "text": "Error Log" }
            }]
        }
        try:
            # Use the hardcoded DISCORD_WEBHOOK_URL for the error message
            response = requests.post(DISCORD_WEBHOOK_URL, json=error_payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send error message to default Discord webhook: {e}")

    else:

        payload = {
            "embeds": [
                {
                    "title": f"{symbol} – {title}",
                    "fields": [
                        {
                            "name": "Description",
                            "value": description,
                            "inline": False
                        },
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
                    "color": color,
                    "timestamp": time,
                    "footer": {
                        "text": "Signal Bot",
                        # Replace with your bot's icon URL. You can use a URL to any image.
                        "icon_url": "https://i.imgur.com/fKL31aD.jpg" 
                    }
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
                    discordLink,
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

def worker():
    """Processes tasks from the queue one by one."""
    while True:
        print("Worker waiting for a task...")
        data = task_queue.get()  # This will block until a task is available
        print(f"Worker picked up a task for symbol: {data.get('symbol')}")
        
        symbol = data.get('symbol')
        timeframe = data.get('timeframe')
        chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

        try:
            screenshot_path = open_browser_and_press_key(
                chart_url, 
                timeframe=timeframe, 
                keys_to_press=(Keys.CONTROL, Keys.ALT, 's')
            )

            if screenshot_path:
                print(f"Screenshot saved to: {screenshot_path}")
                send_to_discord(screenshot_path, data)
                os.remove(screenshot_path)
                print(f"Successfully processed and sent signal for {symbol}.")
            else:
                print(f"ERROR: Failed to download screenshot for {symbol}.")

        except Exception as e:
            tb_str = traceback.format_exc()
            error_message = f"An unexpected error occurred while processing {symbol}: {e}"
            print(f"ERROR: {error_message}\n{tb_str}")
        finally:
            task_queue.task_done() # Signal that the task is finished

@app.route('/', methods=['POST'])
def handle_chart_webhook():
    data = request.get_json()
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Missing 'symbol' in request body"}), 400

    print(f"Received webhook for symbol: {data['symbol']}. Adding to queue.")
    task_queue.put(data)
    return jsonify({"status": "queued", "message": "Chart generation task has been queued."}), 202

if __name__ == '__main__':
    # Start the background worker thread
    # The `daemon=True` flag ensures the thread will exit when the main app exits.
    threading.Thread(target=worker, daemon=True).start()
    app.run(host='0.0.0.0', debug=True)
