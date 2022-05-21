import logging
from pathlib import Path

import pandas as pd
import orjson
import telegram.ext
from telegram.ext import Updater, CommandHandler

from parsing import get_rightmove_feed, get_zoopla_feed
from area_lib import detect_area
from utils import get_hash_from_image_url, get_hash_from_description
from db import DB
from config import TG_TOKEN, TG_CHAT_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = DB("seen_links.json", "seen_hashes.json", "seen_description_hashes.json")
minprices_by_area_num_bedrooms = orjson.loads(Path("minprices_by_area_num_bedrooms.json").read_bytes())

MAX_FLOOR_AREA = 50


def send_message(bot, img_url, epc_url, caption):
    bot.send_media_group(chat_id=TG_CHAT_ID, media=[
        telegram.InputMediaPhoto(img_url, caption=caption),
        telegram.InputMediaPhoto(epc_url),
    ])


def check_and_send_message(bot, link, address, area, number_bedrooms, price, floorplan_url, epc_url):
    send_message(bot, floorplan_url, epc_url,
                 f"{link}\n\nPrice: {price}\nArea: {area}\nNum bedrooms: {number_bedrooms}\n{address}")


def zoopla_job(context: telegram.ext.CallbackContext):
    logger.info("Start parsing zoopla")
    zoopla_flats = get_zoopla_feed(db.seen_links)
    for item in zoopla_flats:
        link = item['url']
        if link not in db:
            db.update(link)

            description_hash = get_hash_from_description(item['description'])
            if not db.contains_description_hash(description_hash):
                db.update_description_hash(description_hash)
            else:
                logger.info(f"Skipping {link} cause of duplicate description")
                continue

            if not pd.isnull(item['floorplan_url']):
                image_hash = get_hash_from_image_url(item['floorplan_url'])
                if not db.contains_hash(image_hash):
                    db.update_hash(image_hash)
                else:
                    logger.info(f"Skipping {link} cause of duplicate image")
                    continue
            else:
                continue

            if pd.isnull(item['epc_url']):
                continue

            total_area = detect_area(item['floorplan_url'])
            if total_area < MAX_FLOOR_AREA and total_area != 0:
                logger.info(f"Skipping {link} cause of small area")
                continue
            else:
                if total_area >= MAX_FLOOR_AREA:
                    total_area_s = f"{total_area:.1f} sq.m"
                else:
                    total_area_s = "unknown"

            check_and_send_message(
                context.bot, link, item['address'],
                total_area_s, item['number_bedrooms'], item['price'], item['floorplan_url'], item['epc_url']
            )

    logger.info("End parsing zoopla")


def rightmove_job(context: telegram.ext.CallbackContext):
    logger.info("Start parsing rightmove")
    flats_df = get_rightmove_feed(db.seen_links)
    for item in flats_df.itertuples():
        link = item.url
        if link not in db:
            db.update(link)

            description = item.full_description if (
                    isinstance(item.full_description, str) and isinstance(item.description, str)
                    and len(item.full_description) > len(item.description)
            ) else item.description
            description_hash = get_hash_from_description(description)
            if not db.contains_description_hash(description_hash):
                db.update_description_hash(description_hash)
            else:
                logger.info(f"Skipping {link} cause of duplicate description")
                continue

            if not pd.isnull(item.floorplan_url):
                image_hash = get_hash_from_image_url(item.floorplan_url)
                if not db.contains_hash(image_hash):
                    db.update_hash(image_hash)
                else:
                    logger.info(f"Skipping {link} cause of duplicate image")
                    continue
            else:
                continue

            if pd.isnull(item.epc_url):
                continue

            total_area = detect_area(item.floorplan_url)
            if total_area < MAX_FLOOR_AREA and total_area != 0:
                logger.info(f"Skipping {link} cause of small area")
                continue
            else:
                if total_area >= MAX_FLOOR_AREA:
                    total_area_s = f"{total_area:.1f} sq.m"
                else:
                    total_area_s = "unknown"

            check_and_send_message(
                context.bot, link, item.address,
                total_area_s, item.number_bedrooms, item.price,
                item.floorplan_url, item.epc_url
            )

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
