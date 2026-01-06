from pluxee import PluxeeClient, PassType
from datetime import date, timedelta
import csv
import requests
import sys
import os

import logging

# Configure logging for verbose Docker output
logging.basicConfig(level=logging.INFO,stream=sys.stdout)
logger = logging.getLogger(__name__)

api_token = os.getenv("API_TOKEN")

#print(f"My API key is: {api_token}")
#logger.info(f"My API key is: {api_token}")

def main():
    # Authenticate
    client = PluxeeClient(EMAIL,PASSWORD)

    # Fetch transactions
    transactions = client.get_transactions(PassType.LUNCH, date.today() - timedelta(days=20), date.today())

    # Prepare cleaned list
    cleaned = []
    for tx in transactions:
        # Split detail by newline and take first line if needed
        description_lines = tx.detail.split('\n') if tx.detail else []
        description = tx.merchant or (description_lines[0] if description_lines else "N/A")

        # Format date as dd-mm-yyyy
        formatted_date = tx.date.strftime("%d-%m-%Y")

        # Prepare row
        cleaned.append([formatted_date, description, f"{tx.amount:.2f}"])
    if "matteo" in EMAIL:
        csv_filename = "matteo_sodexo.csv"
    elif "giulia" in EMAIL:
        csv_filename = "giulia_sodexo.csv"

    # Write to CSV with semicolon separator
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Date", "Description", "Amount"])
        writer.writerows(cleaned)

    logger.info(f"Saved to {csv_filename}")
    print(f"Saved to {csv_filename}")

    return csv_filename

def send_post_request(json_config, csv_file):
    url = 'http://192.168.178.253:6901/autoupload?secret=KRdzb6punx7QwWtF'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }
    files = {
        'importable': (csv_file, open(csv_file, 'rb')),
        'json': (json_config, open(json_config,'rb'))
    }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        print(f"POST request for {csv_file} successful. Status code {response.status_code}.")
        logger.info(f"POST request for {csv_file} successful. Status code {response.status_code}.")
    else:
        logger.info(f"POST request for {csv_file} successful. Status code {response.status_code}.")
        print(f"POST request failed with status code {response.status_code}.")

if __name__ == "__main__":
    for user in ["matteo","giulia"]:
        if user == "matteo":
            EMAIL = "matteo.beg@gmail.com"
            PASSWORD = "001122aA@"
            json_config = "Sodexo_Matteo_config.json"
            csv_filename = main()
            send_post_request(json_config, csv_filename)
        elif user == "giulia":
            json_config = "Sodexo_Giulia_config.json"
            EMAIL = "giuliacaputo0@gmail.com"
            PASSWORD = "Thebeatles92"
            csv_filename = main()
            send_post_request(json_config, csv_filename)
