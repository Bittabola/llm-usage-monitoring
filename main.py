import requests
import time
import os
import logging
import json
from flask import Flask, send_from_directory
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
MQTT_BROKER = os.getenv("MQTT_BROKER", "your_mqtt_broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "homeassistant/sensor/openai_cost")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "your_mqtt_username")  # Added username
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "your_mqtt_password")  # Added password

# Modify fetch_openai_usage to include the required 'date' query parameter
def fetch_openai_usage():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    current_date = datetime.now().strftime("%Y-%m-%d")
    usage_url = f"https://api.openai.com/v1/usage?date={current_date}"

    # Fetch usage data
    response = requests.get(usage_url, headers=headers)
    usage_data = response.json()

    # Extract token usage from response headers or metadata
    token_usage = usage_data.get("total_tokens", "N/A")
    print(f"Token usage: {token_usage}", flush=True)

    return usage_data

# Update generate_html to display token usage
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