import random
import time
import logging

from rightmove_scraper import RightmoveData
from zoopla_scraper import parse_weblink, get_apartments

logger = logging.getLogger(__name__)

DAILY_RIGHTMOVE_URL = r"https://www.rightmove.co.uk/property-to-rent/find.html?minBedrooms=1&keywords=&dontShow=houseShare%2Cretirement%2Cstudent&channel=RENT&index=0&retirement=false&houseFlatShare=false&letType=long_term&maxBedrooms=2&sortType=2&minPrice=1750&viewType=LIST&maxPrice=2250&radius=0.0&maxDaysSinceAdded=1&locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22w%7CvyHjzDpeA%7BhBti%40xfA%7ETyHx_%40e%5D%60Kck%40nd%40g%7C%40xQwOd%5BvRuDllCtO%7C%7E%40ml%40vd%40rE%60sAeKhaAkRtkA%7DD%7CfAuKb_%40uCriAiClhARxsAj%40zfAzX%7CbCdj%40roB%7DiBbzB%7BkAynBm%7BAqz%40%7Dd%40lEkEk%5Eo%7E%40y%5EmJ%7DdCuNogEtv%40sbBjEerArAy%7E%40eB%7Di%40d%5B_%40h%60%40kRsP%7BeCbx%40%7B%7D%40%22%7D"
DAILY_ZOOPLA_URL = r"https://www.zoopla.co.uk/to-rent/property/london/?added=24_hours&beds_max=2&beds_min=1&include_shared_accommodation=false&price_frequency=per_month&price_max=2250&price_min=1750&q=London&radius=0&results_sort=newest_listings&search_source=facets&hidePoly=false&polyenc=_jqyHjgR~r%40oqIni%40as%40%7D%5C%7BkFm%7DBdyD%7Bi%40ybAqbC%7CiCx%5Dx%60CyhA%7CZep%40bcHvYhcIpt%40%7C_AvkCh_AdmAd%7CBptA_pBiWscA%7DI_jA%7BPo_C%7B%40s~C"


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
