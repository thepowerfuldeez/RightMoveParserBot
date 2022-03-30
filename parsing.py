import requests

from scraper import RightmoveData
from config import IDEAL_POSTCODES_API_KEY

RIGHTMOVE_DAILY_URL = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22ecayHh%7Br%40ot%40rt%40cfF~vAioEzKaoBsdFw%7D%40g_L_k%40mkHi%5Ce%7CFrMc%60E%60_AoaA_W%7DaCht%40%7BaCuQchBjPchBj%60AlEl%60BbPltAhCv%7D%40%3FntAen%40fwBor%40jXzmJqpBniIgoBq_BwyAiyBolCb%60EtUduCtUh~Fk%5CvhEveAd%7CF~VljC%7CuCcyArdDaxGdgAknAac%40muDox%40sjDwq%40kwCppBqkIzaAj%7CG%60_%40jmG%60GrjDll%40hyBop%40tcAkLdmFyy%40%7CnDdgAtrAkTjp%40%22%7D&maxBedrooms=2&minBedrooms=1&maxPrice=2000&minPrice=1500&propertyTypes=flat&primaryDisplayPropertyType=flats&maxDaysSinceAdded=1&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=unfurnished&letType=longTerm&keywords="


def get_rightmove_feed(seen_links):
    rm_data = RightmoveData(RIGHTMOVE_DAILY_URL)
    rm_data.set_seen_links(seen_links)
    flats_df = rm_data.parse(get_floorplans=True)

    return flats_df


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

