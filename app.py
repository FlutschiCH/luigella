from flask import Flask, request, redirect, jsonify

# Import the function from your other script
from browser_automation import open_browser_and_press_key

# Create an instance of the Flask class.
# __name__ is a special Python variable that gives each file a unique name.
app = Flask(__name__)

# This is a "decorator" that turns a regular Python function into a Flask view.
# It maps the URL path '/' (the root of the site) to the hello_world function.
@app.route('/')
def hello_world():
    """This view function returns a string to be displayed in the user's browser."""
    return 'Hello, World!'

@app.route('/webhook/chart', methods=['POST'])
def handle_chart_webhook():
    """
    Accepts a POST request with a JSON payload like {"symbol": "AAPL"}.
    It then opens a browser to a trading chart for that symbol.
    """
    data = request.get_json()
    if not data or 'symbol' not in data:
        # Return an error if the JSON is malformed or missing the 'symbol'
        return jsonify({"status": "error", "message": "Missing 'symbol' in request body"}), 400

    symbol = data['symbol']
    print(f"Received webhook for symbol: {symbol}")

    # Construct the URL using the symbol from the webhook
    # I'm using TradingView as an example target site.
    chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"

    try:
        # Call the browser automation function with the generated URL
        # For this example, we'll just send the ESCAPE key to close any pop-ups.
        from selenium.webdriver.common.keys import Keys
        open_browser_and_press_key(chart_url, Keys.ESCAPE)
        return jsonify({"status": "success", "message": f"Browser automation started for {symbol}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred during browser automation: {e}"}), 500

# This block ensures the server only runs when the script is executed directly.
if __name__ == '__main__':
    app.run(debug=True)
