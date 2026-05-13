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
RETRY_ATTEMPTS = 3
RETRY_DELAY = 10  # seconds between retries
 
def fetch_page(url, params, feed_name, page_num):
    """Fetch a single page with retries on 5xx errors."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)

            # Retry on server errors
            if response.status_code >= 500:
                logger.warning("%s feed page %d: server error %d, attempt %d/%d",
                               feed_name, page_num, response.status_code, attempt, RETRY_ATTEMPTS)
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    logger.error("%s feed page %d: giving up after %d attempts",
                                 feed_name, page_num, RETRY_ATTEMPTS)
                    return None

            response.raise_for_status()

            if not response.text.strip():
                logger.warning("%s feed page %d: empty response, stopping.", feed_name, page_num)
                return None

            return response.json()

        except requests.exceptions.Timeout:
            logger.warning("%s feed page %d: timeout, attempt %d/%d",
                           feed_name, page_num, attempt, RETRY_ATTEMPTS)
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)
            else:
                return None

    return None


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

        data = fetch_page(url, params, feed_name, page_num)

        # None means the page failed or was empty — stop pagination
        if data is None:
            logger.info("%s feed: stopping at page %d.", feed_name, page_num)
            break

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
        time.sleep(1)

    total = len(combined.get("data", {}).get("listings", []))
    logger.info("%s feed complete: %d total listings", feed_name, total)
    return combined, total


def save_feed(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info("Saved: %s", output_path)


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "bronze_layer/assets"

    failed = []
    for feed_name, url in FEEDS.items():
        try:
            data, total = fetch_feed(feed_name, url)
            if total == 0:
                logger.error("%s feed: no listings fetched, skipping save.", feed_name)
                failed.append(feed_name)
            else:
                save_feed(data, os.path.join(output_dir, f"{feed_name}_data.json"))
        except Exception as e:
            logger.error("Failed to fetch %s feed: %s", feed_name, e)
            failed.append(feed_name)

    if failed:
        logger.error("The following feeds failed: %s", failed)
        # Warn but don't exit with code 1 if at least one feed succeeded
        if len(failed) == len(FEEDS):
            sys.exit(1)  # all feeds failed — block the pipeline
        else:
            logger.warning("Partial success — continuing pipeline with available data.")