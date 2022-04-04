import random
import time

import requests

from rightmove_scraper import RightmoveData
from zoopla_scraper import parse_weblink, get_apartments
from config import IDEAL_POSTCODES_API_KEY

DAILY_RIGHTMOVE_URL = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22y%7CpyH%60aSjF_xAR%7DfAtD%7D%7DAk%5Dih%40kj%40sHugAf%60%40kx%40%60e%40_e%40jmAjI~tBuG~r%40~A%60_B~Vhw%40h%60%40re%40vlA%60e%40j_Al%5BjUfBkDimAi%40sbA~AifAhDkw%40%22%7D&maxBedrooms=2&minBedrooms=1&maxPrice=2000&minPrice=1500&radius=0.25&propertyTypes=flat&primaryDisplayPropertyType=flats&maxDaysSinceAdded=1&mustHave=&dontShow=student%2Cretirement%2ChouseShare&furnishTypes=&letType=longTerm&keywords="
DAILY_ZOOPLA_URL = r"https://www.zoopla.co.uk/to-rent/flats/london/?added=24_hours&beds_max=2&beds_min=1&include_shared_accommodation=false&page_size=25&polyenc=ujqyHzkS`UolEu^imAmfAo\uoAre@_l@`pDhNvuC~_@bfCpu@hiAzl@fF`bAc^aFeuF&price_frequency=per_month&price_max=2000&price_min=1500&view_type=list&q=London&radius=0.25&results_sort=newest_listings&search_source=refine"


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


def get_zoopla_feed(seen_links):
    results = []
    for weblink in get_apartments(DAILY_ZOOPLA_URL):
        if weblink in seen_links:
            continue
        time.sleep(random.random() * 2)
        res = parse_weblink(weblink)
        if res and res['floorplan_url']:
            results.append(res)
    return results


def get_rightmove_feed(seen_links):
    rm_data = RightmoveData(DAILY_RIGHTMOVE_URL)
    rm_data.set_seen_links(seen_links)
    flats_df = rm_data.parse(get_floorplans=True)

    return flats_df
