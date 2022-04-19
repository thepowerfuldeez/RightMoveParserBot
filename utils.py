import random
import hashlib

import pandas as pd
import requests
from PIL import Image
from imagehash import phash

from config import IDEAL_POSTCODES_API_KEY
from parsing import logger


def fill_postcode(address_query):
    if not address_query.endswith(", London"):
        address_query += ", London"
    params = {"api_key": IDEAL_POSTCODES_API_KEY, "query": address_query}

    r = requests.get("https://api.ideal-postcodes.co.uk/v1/addresses", params=params)
    hits = r.json()
    if "result" in hits and "hits" in hits['result']:
        results = hits['result']['hits']
        full_postcode = results[0]['postcode']
        postcode = results[0]['postcode_outward']
        return postcode


def fill_postcode_from_address(postcode, address):
    if pd.isnull(postcode):
        logger.info("Postcode is null, try to fill using external service")
        postcode = fill_postcode(address)
        if postcode is not None:
            logger.info(f"Postcode is filled ({postcode})")
        else:
            logger.info("Postcode is not filled")
            return
    return postcode


def get_hash_from_description(description):
    if not isinstance(description, str):
        description_str = description.strip().lower()
    else:
        description_str = str(random.random())
    description_hash = hashlib.sha256(description_str.encode('utf-8')).hexdigest()[:8]
    return description_hash


def get_hash_from_image_url(image_url):
    try:
        image = Image.open(requests.get(image_url, stream=True).raw)
        return str(phash(image))[:8]
    except Exception as e:
        print("using random hash")
        # if not image – return random hash
        return str(hash(image_url))[:8]
