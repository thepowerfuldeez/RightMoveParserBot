import orjson

from typing import Union
from pathlib import Path


class DB:
    def __init__(self, save_path: Union[str, Path]):
        if isinstance(save_path, str):
            save_path = Path(save_path)
        self.save_path = save_path

        seen_links = dict()
        if save_path.exists():
            seen_links = orjson.loads(save_path.read_bytes())
        self.seen_links = seen_links

    def update(self, link):
        if link not in self.seen_links:
            self.seen_links[link] = 1
            self.save_path.write_bytes(orjson.dumps(self.seen_links))

    def __contains__(self, link):
        return link in self.seen_links
