import random
import time
import logging

from rightmove_scraper import RightmoveData
from zoopla_scraper import parse_weblink, get_apartments

logger = logging.getLogger(__name__)

DAILY_RIGHTMOVE_URL = r"https://www.rightmove.co.uk/property-to-rent/find.html?minBedrooms=1&keywords=&channel=RENT&index=0&letType=long_term&maxBedrooms=2&sortType=2&minPrice=1750&viewType=LIST&maxPrice=2250&radius=0.25&maxDaysSinceAdded=1&locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22%7DbvyH%7ClYi%60%40se%40_Wiw%40_Ba_BtG_s%40ds%40wXeVknAkh%40giBtn%40uvAjeA_g%40j%60Ase%40t_%40fF%60bAhVdLb%7DAq%60%40nu%40kRtkA%7DD%7CfAkF%7EwAiDjw%40_BhfAh%40rbAjDhmAkUgBk_Am%5BwlAae%40%22%7D"
DAILY_ZOOPLA_URL = r"https://www.zoopla.co.uk/to-rent/flats/london/?added=24_hours&beds_max=2&beds_min=1&include_shared_accommodation=false&page_size=25&polyenc=ujqyHzkS`YgkDf{@yjBgnAchBas@yNat@nQkTnhAor@jb@yGdkAnWp|Boh@`Ohe@`sFpu@hiAzl@fF`bAc^aFeuF&price_frequency=per_month&price_max=2250&price_min=1750&view_type=list&q=London&radius=0&results_sort=newest_listings&search_source=refine"


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
