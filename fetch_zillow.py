import requests
import json
import os
import logging
import sys
import time
from dotenv import load_dotenv
 
load_dotenv()
 
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
 
HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": "real-estate-zillow-com.p.rapidapi.com",
    "Content-Type": "application/json"
}
 
FEEDS = {
    "sale": "https://real-estate-zillow-com.p.rapidapi.com/v1/search/sale",
    "rent": "https://real-estate-zillow-com.p.rapidapi.com/v1/search/rent",
}
 
LOCATION = os.getenv("ZILLOW_LOCATION", "new mexico")
MAX_PAGES = int(os.getenv("ZILLOW_MAX_PAGES", "24"))
 
 
def fetch_feed(feed_name, url):
    """Fetch all pages for a single feed and return combined results."""
    combined = {}
    for page_num in range(1, MAX_PAGES + 1):
        params = {
            "location_or_rid": LOCATION,
            "property_types": "house",
            "sort": "relevant",
            "page": str(page_num)
        }
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        # Handle empty response body — API sometimes returns nothing on rate limit
        if not response.text.strip():
            logger.warning("%s feed: empty response on page %d, stopping.", feed_name, page_num)
            break

        data = response.json()

        listings = data.get("data", {}).get("listings", [])
        if not listings:
            logger.info("%s feed: no listings on page %d, stopping.", feed_name, page_num)
            break

        if not combined:
            combined = data
        else:
            combined["data"]["listings"].extend(listings)

        logger.info("%s feed: fetched page %d (%d listings so far)",
                    feed_name, page_num, len(combined["data"]["listings"]))
        time.sleep(1)  # Sleep to respect API rate limits

    total = len(combined.get("data", {}).get("listings", []))
    logger.info("%s feed complete: %d total listings", feed_name, total)
    return combined
 
 
def save_feed(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info("Saved: %s", output_path)
 
 
if __name__ == "__main__":
    # Output directory can be overridden via CLI arg, defaults to bronze_layer/assets
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "bronze_layer/assets"
 
    failed = []
    for feed_name, url in FEEDS.items():
        try:
            data = fetch_feed(feed_name, url)
            save_feed(data, os.path.join(output_dir, f"{feed_name}_data.json"))
        except Exception as e:
            logger.error("Failed to fetch %s feed: %s", feed_name, e)
            failed.append(feed_name)
 
    if failed:
        logger.error("The following feeds failed: %s", failed)
        sys.exit(1)
 
    logger.info("All feeds fetched successfully.")