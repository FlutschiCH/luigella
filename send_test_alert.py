import requests
import json
from datetime import datetime
import sys

# --- Configuration ---
# This is the default webhook ID to use if none is provided via the command line.
DEFAULT_WEBHOOK_ID = "5a5jgsbd2iccwh81fmebxq1cp3cd7on9"

# These are the values for the JSON payload you want to send.
TEST_TICKER = "BTCUSD"      # Corresponds to "symbol" in the payload
TEST_INTERVAL = "15"        # Corresponds to "timeframe"
TEST_PRICE = 65000.00       # Corresponds to "price"
TEST_EXCHANGE = "BINANCE"   # Corresponds to "exchange"
TEST_DIVERGENCE = "bullish" # Corresponds to "divergenz"

# The address of your running Flask application.
# If you are running this script on the same machine as the server, 127.0.0.1 is correct.
# If running from another computer on the same network, replace 127.0.0.1 with the server's local IP address.
SERVER_ADDRESS = "http://5.147.217.198"
# SERVER_ADDRESS = "http://127.0.0.1:5000"
# --- End Configuration ---

def send_test_alert():
    """
    Sends a test POST request to the running Flask application
    to trigger the chart generation and webhook forwarding process.
    """
    # Use the webhook ID from the command line if provided, otherwise use the default.
    if len(sys.argv) > 1:
        webhook_id = sys.argv[1]
        print(f"Using webhook ID from command line: {webhook_id}")
    else:
        webhook_id = DEFAULT_WEBHOOK_ID

    url = f"{SERVER_ADDRESS}/{webhook_id}"
    
    # Build the payload based on the configuration above
    payload = {
        "symbol": TEST_TICKER,
        "timeframe": TEST_INTERVAL,
        "price": TEST_PRICE,
        "exchange": TEST_EXCHANGE,
        "timenow": datetime.now().isoformat(), # Generates the current time automatically
        "divergenz": TEST_DIVERGENCE
    }

    print(f"Sending POST request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, timeout=20) # Increased timeout for potentially long operations
        print("\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("\n--- Error ---")
        print(f"Failed to connect to the server: {e}")
        print("Please make sure the 'app.py' server is running and accessible at the configured address.")

if __name__ == "__main__":
    send_test_alert()