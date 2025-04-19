import requests
import time
import os
import logging
import json
from flask import Flask, send_from_directory
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please add it to the .env file.")

def fetch_openai_usage():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    mountain_tz = pytz.timezone("US/Mountain")
    usage_data = {"data": []}

    # Fetch data for the last 30 days
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        usage_url = f"https://api.openai.com/v1/usage?date={date}"

        response = requests.get(usage_url, headers=headers)
        if response.status_code == 200:
            daily_data = response.json().get("data", [])
            usage_data["data"].extend(daily_data)
        else:
            print(f"Error fetching usage data for {date}: {response.json()}", flush=True)

    print(f"Fetched usage data: {usage_data}", flush=True)
    return usage_data

def generate_html(usage_data):
    mountain_tz = pytz.timezone("US/Mountain")
    table_rows = ""
    for entry in usage_data.get("data", []):
        timestamp = entry.get('aggregation_timestamp', 'N/A')
        human_readable_timestamp = datetime.fromtimestamp(timestamp, mountain_tz).strftime('%Y-%m-%d %H:%M:%S') if timestamp != 'N/A' else 'N/A'
        table_rows += f"""
        <tr>
            <td>{human_readable_timestamp}</td>
            <td>{entry.get('operation', 'N/A')}</td>
            <td>{entry.get('n_requests', 'N/A')}</td>
            <td>{entry.get('n_context_tokens_total', 'N/A')}</td>
            <td>{entry.get('n_generated_tokens_total', 'N/A')}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OpenAI Token Usage</title>
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .pagination {{
            margin-top: 20px;
            text-align: center;
        }}
        .pagination button {{
            margin: 0 5px;
            padding: 5px 10px;
            cursor: pointer;
        }}
    </style>
    <script>
        let currentPage = 1;
        const rowsPerPage = 20;

        function showPage(page) {{
            const rows = document.querySelectorAll("tbody tr");
            const totalRows = rows.length;
            const totalPages = Math.ceil(totalRows / rowsPerPage);

            // Ensure page is within valid range
            if (page < 1 || page > totalPages) return;

            // Update page info
            document.getElementById("page-info").innerText = `Page ${page} of ${totalPages}`;

            rows.forEach((row, index) => {{
                row.style.display = (index >= (page - 1) * rowsPerPage && index < page * rowsPerPage) ? "" : "none";
            }});

            currentPage = page;
        }}

        function nextPage() {{
            const rows = document.querySelectorAll("tbody tr");
            const totalPages = Math.ceil(rows.length / rowsPerPage);
            if (currentPage < totalPages) showPage(currentPage + 1);
        }}

        function prevPage() {{
            if (currentPage > 1) showPage(currentPage - 1);
        }}

        document.addEventListener("DOMContentLoaded", () => {{
            const rows = document.querySelectorAll("tbody tr");
            const totalPages = Math.ceil(rows.length / rowsPerPage);
            document.getElementById("page-info").innerText = `Page 1 of ${totalPages}`;
            showPage(1);
        }});
    </script>
</head>
<body>
    <h1>OpenAI Token Usage</h1>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Operation</th>
                <th>Requests</th>
                <th>Context Tokens</th>
                <th>Generated Tokens</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    <div class="pagination">
        <button onclick="prevPage()">Previous</button>
        <span id="page-info"></span>
        <button onclick="nextPage()">Next</button>
    </div>
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