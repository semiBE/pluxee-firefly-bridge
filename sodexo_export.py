from pluxee import PluxeeClient, PassType
from datetime import date, timedelta
import csv
import requests
import sys
import os

import logging

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# 1. Get the absolute path of the directory where sodexo_export.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging for verbose Docker output
logging.basicConfig(level=logging.INFO,stream=sys.stdout)
logger = logging.getLogger(__name__)

api_token = os.environ.get("API_TOKEN")
mat_email = os.environ.get("MAT_EMAIL")
mat_pwd = os.environ.get("MAT_PWD")
giu_email = os.environ.get("GIU_EMAIL")
giu_pwd = os.environ.get("GIU_PWD")
url = os.environ.get("URL")

logger.info(f"Target URL: {url}")
logger.info(f"Token Length: {len(api_token) if api_token else 'EMPTY'}")
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
        csv_filename = "mat_sodexo.csv"
    elif "giulia" in EMAIL:
        csv_filename = "giu_sodexo.csv"

    # Write to CSV with semicolon separator
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Date", "Description", "Amount"])
        writer.writerows(cleaned)

    logger.info(f"Saved to {csv_filename}")
    print(f"Saved to {csv_filename}")

    # --- New: Print and Log CSV Content ---
    print("\n--- CSV Content Preview ---")
    header = "Date, Description, Amount"
    print(header)
    
    for row in cleaned:
        row_str = ", ".join(row)
        print(row_str)
    print("---------------------------\n")
    # --------------------------------------

    return csv_filename

def send_post_request(json_config, csv_file):
    # 2. Construct absolute paths for both files
    json_path = os.path.join(BASE_DIR, json_config)
    csv_path = os.path.join(BASE_DIR, csv_file)
    # 3. Debugging: Log exactly where we are looking
    logger.info(f"Looking for JSON config at: {json_path}")
    logger.info(f"Looking for CSV file at: {csv_path}")

    if not os.path.exists(json_path):
        logger.error(f"FILE NOT FOUND: {json_path}")
        # List files in directory to help debug via logs
        logger.info(f"Files available in {BASE_DIR}: {os.listdir(BASE_DIR)}")
        return

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }
    with open(csv_path, 'rb') as f_csv, open(json_path, 'rb') as f_json:
        files = {
            'importable': (csv_file, f_csv, 'text/csv'),
            'json': (json_config, f_json, 'application/json')
        }
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        print(f"POST request for {csv_file} successful. Status code {response.status_code}.")
        logger.info(f"POST request for {csv_file} successful. Status code {response.status_code}.")
    else:
        logger.info(f"POST request for {csv_file} failed. Status code {response.status_code}.")
        print(f"POST request failed with status code {response.status_code}.")

if __name__ == "__main__":
    for user in ["matteo","giulia"]:
        if user == "matteo":
            EMAIL = mat_email
            PASSWORD = mat_pwd
            json_config = "Sodexo_Mat_config.json"
            csv_filename = main()
            send_post_request(json_config, csv_filename)
        elif user == "giulia":
            json_config = "Sodexo_Giu_config.json"
            EMAIL = giu_email
            PASSWORD = giu_pwd
            csv_filename = main()
            send_post_request(json_config, csv_filename)
