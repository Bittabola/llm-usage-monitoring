import requests
import paho.mqtt.client as mqtt
import time
import os

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
MQTT_BROKER = os.getenv("MQTT_BROKER", "your_mqtt_broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "homeassistant/sensor/openai_cost")

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

# Function to publish data to MQTT
def publish_to_mqtt(usage_data, credits_data):
    client = mqtt.Client(protocol=mqtt.MQTTv311)  # Updated to specify protocol version
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Prepare payload
    payload = {
        "usage": usage_data,
        "credits": credits_data
    }

    client.publish(MQTT_TOPIC, str(payload))
    client.disconnect()

# Main loop
def main():
    while True:
        usage_data, credits_data = fetch_openai_usage()
        publish_to_mqtt(usage_data, credits_data)
        time.sleep(3600)  # Run every hour

if __name__ == "__main__":
    main()