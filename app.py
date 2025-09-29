# pip install -r requirements.txt


from flask import Flask, request, redirect, jsonify
import requests
import os

from browser_automation import open_browser_and_press_key

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your/webhook_url_here"

app = Flask(__name__)

def send_to_discord(file_path, symbol):
    if not file_path or not os.path.exists(file_path):
        print(f"Error: Screenshot file not found at {file_path}")
        return

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'image/png')}
        payload = {'content': f'Chart screenshot for **{symbol}**'}
        response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
        print(f"Discord response: {response.status_code} - {response.text}")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webhook/chart', methods=['POST'])
def handle_chart_webhook():
    data = request.get_json()
    if not data or 'symbol' not in data:
        return jsonify({"status": "error", "message": "Missing 'symbol' in request body"}), 400

    symbol = data['symbol']
    print(f"Received webhook for symbol: {symbol}")

    chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

    try:
        from selenium.webdriver.common.keys import Keys
        screenshot_path = open_browser_and_press_key(chart_url, Keys.CONTROL, Keys.ALT, 's')

        if screenshot_path:
            print(f"Screenshot saved to: {screenshot_path}")
            send_to_discord(screenshot_path, symbol)
            os.remove(screenshot_path)
            return jsonify({"status": "success", "message": f"Screenshot for {symbol} sent to Discord."})
        else:
            return jsonify({"status": "error", "message": "Failed to download screenshot."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
