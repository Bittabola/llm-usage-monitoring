import requests
import time
import os
import logging
import json
from flask import Flask, send_from_directory
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please add it to the .env file.")

# Modify fetch_openai_usage to use the 'date' query parameter
def fetch_openai_usage():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    today = datetime.now()
    usage_url = f"https://api.openai.com/v1/usage?date={today.strftime('%Y-%m-%d')}"

    # Fetch usage data
    response = requests.get(usage_url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching usage data: {response.json()}", flush=True)
        return {"error": response.json()}

    usage_data = response.json()

    # Handle empty responses
    if not usage_data.get("data"):
        usage_data["message"] = "No usage data available for the specified date."

    print(f"Fetched usage data: {usage_data}", flush=True)

    return usage_data

# Update generate_html to display a message if no data is available
def generate_html(usage_data):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OpenAI Token Usage</title>
</head>
<body>
    <h1>OpenAI Token Usage</h1>
    <pre>{json.dumps(usage_data, indent=4)}</pre>
</body>
</html>"""

    with open("./usage_data.html", "w") as html_file:
        html_file.write(html_content)
    print("Saving HTML file to ./usage_data.html", flush=True)

# Create a Flask app
app = Flask(__name__)

# Ensure the generated HTML file is served correctly
@app.route('/')
def serve_html():
    return send_from_directory('.', 'usage_data.html')

@app.route('/usage_data.html')
def serve_usage_data():
    return send_from_directory('.', 'usage_data.html')

# Main loop
def main():
    while True:
        usage_data = fetch_openai_usage()
        generate_html(usage_data)
        time.sleep(3600)  # Run every hour

# Update main to reflect token usage tracking
if __name__ == "__main__":
    usage_data = fetch_openai_usage()
    generate_html(usage_data)
    app.run(host='0.0.0.0', port=5000)