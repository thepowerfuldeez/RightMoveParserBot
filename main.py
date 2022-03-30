import logging
from pathlib import Path

import pandas as pd
import orjson
import telegram.ext
from telegram.ext import Updater, CommandHandler

from parsing import get_rightmove_feed, fill_postcode
from db import DB
from config import TG_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = DB("seen_links.json")
minprices_by_area_num_bedrooms = orjson.loads(Path("minprices_by_area_num_bedrooms.json").read_bytes())


def send_message(bot, img_url, caption):
    bot.send_photo(chat_id="@instantflats", photo=img_url, caption=caption)


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

            k = f"{postcode}_{item.number_bedrooms}"
            if (
                    k in minprices_by_area_num_bedrooms
                    and item.price <= minprices_by_area_num_bedrooms[k]
                    and not pd.isnull(item.floorplan_url)
            ):
                send_message(context.bot, item.floorplan_url,
                             f"{link}\n\nPrice: {item.price}\nNum bedrooms: {item.number_bedrooms}\n{item.address}")
    logger.info("End parsing rightmove")


def main():
    logger.info("starting to work")
    updater = Updater(TG_TOKEN, use_context=True)
    job_queue = updater.job_queue
    job_queue.run_repeating(rightmove_job, interval=600, first=0)
    job_queue.start()


if __name__ == '__main__':
    main()


