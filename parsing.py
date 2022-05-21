import random
import time
import logging

from rightmove_scraper import RightmoveData
from zoopla_scraper import parse_weblink, get_apartments

logger = logging.getLogger(__name__)

DAILY_RIGHTMOVE_URL = r"https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22kpsyH~p_%40oj%40xfBm%7BAqz%40%7Dd%40lEkEk%5Eo~%40y%5EmJ%7DdCuNogEtv%40sbBjEerArAy~%40eB%7Di%40d%5B_%40h%60%40kRsP%7BeCbx%40%7B%7D%40peA%7BhBti%40xfA~TyHx_%40e%5D%60Kck%40nd%40g%7C%40xQwOd%5BvRuDllCtO%7C~%40ml%40vd%40rE%60sAeKhaAkRtkA%7DD%7CfAuKb_%40uCriAiClhARxsAj%40zfAko%40hD%7BUvqC%22%7D&maxBedrooms=2&minBedrooms=1&maxPrice=2250&minPrice=1750&sortType=2&propertyTypes=&maxDaysSinceAdded=1&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=&letType=longTerm&keywords="
DAILY_ZOOPLA_URL = r"https://www.zoopla.co.uk/to-rent/property/london/?added=24_hours&beds_max=2&beds_min=1&include_shared_accommodation=false&price_frequency=per_month&price_max=2250&price_min=1750&q=London&radius=0&results_sort=newest_listings&search_source=facets&hidePoly=false&polyenc=_jqyHjgRfw%40gnFgCgbBni%40as%40uCwlA%7DBogBiTsu%40%7DSlKic%40rfBedAbeAwMig%40c%5BoZwgAnwAyy%40lq%40x%5Dx%60CyhA%7CZep%40bcH~Hd_EvObcCpt%40%7C_Ajw%40dBnf%40ji%40zk%40vQxw%40yoCdAkaBlR%7D%5Dnb%40_BeDmmC"


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
