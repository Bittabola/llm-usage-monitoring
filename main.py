import paho.mqtt
print(f"paho-mqtt version: {paho.mqtt.__version__}", flush=True)

import requests
import paho.mqtt.client as mqtt
import time
import os
import logging
import paho.mqtt
import json

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
MQTT_BROKER = os.getenv("MQTT_BROKER", "your_mqtt_broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "homeassistant/sensor/openai_cost")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "your_mqtt_username")  # Added username
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "your_mqtt_password")  # Added password

# Function to fetch OpenAI API usage
def fetch_openai_usage():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    usage_url = "https://api.openai.com/v1/dashboard/billing/usage"
    credits_url = "https://api.openai.com/v1/dashboard/billing/credit_grants"

    # Fetch usage data
    usage_response = requests.get(usage_url, headers=headers)
    usage_data = usage_response.json()

    # Fetch credits data
    credits_response = requests.get(credits_url, headers=headers)
    credits_data = credits_response.json()

    return usage_data, credits_data

# Function to generate HTML file
def generate_html(usage_data, credits_data):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OpenAI Usage</title>
</head>
<body>
    <h1>OpenAI Usage Data</h1>
    <h2>Usage</h2>
    <pre>{json.dumps(usage_data, indent=4)}</pre>
    <h2>Credits</h2>
    <pre>{json.dumps(credits_data, indent=4)}</pre>
</body>
</html>"""

    with open("usage_data.html", "w") as html_file:
        html_file.write(html_content)

# Main loop
def main():
    while True:
        usage_data, credits_data = fetch_openai_usage()
        generate_html(usage_data, credits_data)
        time.sleep(3600)  # Run every hour

if __name__ == "__main__":
    main()