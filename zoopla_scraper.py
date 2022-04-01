import json
import re

import requests
from lxml import html


def get_apartments(url):
    text = requests.get(url).content
    tree = html.fromstring(text)
    return [f"https://www.zoopla.co.uk{l}" for l in
            tree.xpath("""//*[starts-with(@id, "listing_")]/div/div[2]/div[2]/a[2]/@href""")]


def parse_weblink(weblink):
    text = requests.get(weblink).content
    tree = html.fromstring(text)

    x = json.loads(tree.xpath("""//*[@id="__NEXT_DATA__"]/text()""")[0])
    details = x['props']['pageProps']['listingDetails']
    description = details['detailedDescription']
    address = details['displayAddress']
    pat = r"\b([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?)\b"
    postcode_search = re.findall(pat, address)
    if postcode_search:
        postcode = postcode_search[0]
    else:
        postcode = None

    if details['adTargeting']['hasFloorplan']:
        if details['floorPlan']['pdf']:
            img_url = details['floorPlan']['pdf'][0]['original']
        elif details['floorPlan']['image']:
            img_url = f"https://lc.zoocdn.com/{details['floorPlan']['image'][0]['filename']}"
        elif details['floorPlan']['links']:
            img_url = details['floorPlan']['links'][0]

        num_bedrooms = details['counts']['numBedrooms']
        price = details['pricing']['label'].split()[0]
        if price.startswith("£"):
            price = price[1:]
            price = int(price.replace(",", ""))
        return {"url": weblink,
                "description": description,
                "address": address,
                "postcode": postcode,
                "floorplan_url": img_url,
                "number_bedrooms": num_bedrooms,
                "price": price}
