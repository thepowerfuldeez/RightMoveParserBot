import logging
import hashlib
import random
from pathlib import Path

import pandas as pd
import orjson
import telegram.ext
from telegram.ext import Updater, CommandHandler

from parsing import get_rightmove_feed, fill_postcode, get_zoopla_feed
from db import DB
from config import TG_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = DB("seen_links.json", "seen_hashes.json")
minprices_by_area_num_bedrooms = orjson.loads(Path("minprices_by_area_num_bedrooms.json").read_bytes())


def send_message(bot, img_url, caption):
    bot.send_photo(chat_id="@instantflats", photo=img_url, caption=caption)


def check_and_send_message(bot, link,
                           address, postcode, number_bedrooms, price, description, floorplan_url):
    k = f"{postcode}_{number_bedrooms}"
    if not isinstance(description, str):
        description_str = description.strip().lower()
    else:
        description_str = str(random.random())
    description_hash = hashlib.sha256(description_str.encode('utf-8')).hexdigest()[:8]
    if (
            k in minprices_by_area_num_bedrooms
            and price <= minprices_by_area_num_bedrooms[k]
            and not pd.isnull(floorplan_url)
            and not db.contains_hash(description_hash)
    ):
        db.update_hash(description_hash)
        send_message(bot, floorplan_url,
                     f"{link}\n\nPrice: {price}\nNum bedrooms: {number_bedrooms}\n{address}")


def zoopla_job(context: telegram.ext.CallbackContext):
    logger.info("Start parsing zoopla")
    zoopla_flats = get_zoopla_feed(db.seen_links)
    for item in zoopla_flats:
        link = item['url']
        if link not in db:
            db.update(link)

            postcode = item['postcode']
            if pd.isnull(postcode):
                logger.info("Postcode is null, try to fill using external service")
                postcode = fill_postcode(item['address'])
                if postcode is not None:
                    logger.info(f"Postcode is filled ({postcode})")
                else:
                    logger.info("Postcode is not filled")
                    continue

            check_and_send_message(
                context.bot, link, item['address'],
                postcode, item['number_bedrooms'], item['price'], item['description'], item['floorplan_url'])

    logger.info("End parsing zoopla")


def rightmove_job(context: telegram.ext.CallbackContext):
    logger.info("Start parsing rightmove")
    flats_df = get_rightmove_feed(db.seen_links)
    for item in flats_df.itertuples():
        link = item.url
        if link not in db:
            db.update(link)

            postcode = item.postcode
            if pd.isnull(postcode):
                logger.info("Postcode is null, try to fill using external service")
                postcode = fill_postcode(item.address)
                if postcode is not None:
                    logger.info(f"Postcode is filled ({postcode})")
                else:
                    logger.info("Postcode is not filled")
                    continue

            check_and_send_message(
                context.bot, link, item.address,
                postcode, item.number_bedrooms, item.price,
                item.full_description if (
                        isinstance(item.full_description, str) and isinstance(item.description,str)
                        and len(item.full_description) > len(item.description)
                ) else item.description,
                item.floorplan_url)

    logger.info("End parsing rightmove")


def main():
    logger.info("starting to work")
    updater = Updater(TG_TOKEN, use_context=True)
    job_queue = updater.job_queue
    job_queue.run_repeating(rightmove_job, interval=600, first=0)
    job_queue.run_repeating(zoopla_job, interval=720, first=30)
    job_queue.start()


if __name__ == '__main__':
    main()
