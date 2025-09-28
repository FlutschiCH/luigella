from flask import Flask, request, redirect

# Create an instance of the Flask class.
# __name__ is a special Python variable that gives each file a unique name.
app = Flask(__name__)

# This is a "decorator" that turns a regular Python function into a Flask view.
# It maps the URL path '/' (the root of the site) to the hello_world function.
@app.route('/')
def hello_world():
    """This view function returns a string to be displayed in the user's browser."""
    return 'Hello, World!'

@app.route('/webhook', methods=['POST'])
def webhook_redirect():
    """
    Accepts a POST request (like a webhook) and redirects it to another URL,
    preserving the method and body.
    """
    # You can optionally inspect the webhook data before redirecting
    # print(f"Received webhook data: {request.json}")

    # Redirect to the new destination. Using a 307 status code
    # ensures the client re-sends the POST request with its body.
    return redirect("https://example.com/new-webhook-destination", code=307)

# This block ensures the server only runs when the script is executed directly.
if __name__ == '__main__':
    app.run(debug=True)
