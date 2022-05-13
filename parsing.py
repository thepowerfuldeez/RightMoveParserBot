import random
import time
import logging

from rightmove_scraper import RightmoveData
from zoopla_scraper import parse_weblink, get_apartments

logger = logging.getLogger(__name__)

DAILY_RIGHTMOVE_URL = r"https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22ebsyHziFTye%40ttAqn%40fTphBrE%60sAeKhaAkRtkA%7DD%7CfAuKb_%40uCriAiClhARxsAj%40zfAko%40hD%7BUvqCoj%40xfBm%7BAqz%40%7Dd%40lEkEk%5E%60%40_uL%5EgbBhDabAoEmTy%40a%5Era%40%7DK%60pAgd%40o%40uz%40ne%40w%5Dti%40_%5C%22%7D&maxBedrooms=2&minBedrooms=1&maxPrice=2250&minPrice=1750&propertyTypes=&maxDaysSinceAdded=1&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=&letType=longTerm&keywords="
DAILY_ZOOPLA_URL = r"https://www.zoopla.co.uk/to-rent/property/london?added=24_hours&beds_max=2&beds_min=1&include_shared_accommodation=false&page_size=25&polyenc=_jqyHjgRhF%7Dt%40jLunAbG%7BqAlZwUoQsdFmbB%7EcAnBzg%40%7DlAtd%40%7ENxo%40or%40dn%40ulA%7ELz%40rmCr%40jwFkAh%60HfcB%7C%60%40xh%40nAlYkeA%60%5Cqm%40vTkhGd%5DkH&price_frequency=per_month&price_max=2250&price_min=1750&view_type=list&q=London&radius=0&results_sort=newest_listings&search_source=facets"


def get_zoopla_feed(seen_links):
    results = []
    for weblink in get_apartments(DAILY_ZOOPLA_URL):
        if weblink in seen_links:
            continue
        time.sleep(random.random() * 2)
        res = parse_weblink(weblink)
        if res and res['floorplan_url'] and res['epc_url']:
            results.append(res)
    return results


def get_rightmove_feed(seen_links):
    rm_data = RightmoveData(DAILY_RIGHTMOVE_URL)
    rm_data.set_seen_links(seen_links)
    flats_df = rm_data.parse(get_floorplans=True)

    return flats_df
