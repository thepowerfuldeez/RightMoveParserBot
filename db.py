import orjson

from typing import Union
from pathlib import Path


class DB:
    def __init__(self, save_path: Union[str, Path], hash_save_path: Union[str, Path],
                 description_hash_save_path: Union[str, Path]):
        if isinstance(save_path, str):
            save_path = Path(save_path)
        self.save_path = save_path

        seen_links = dict()
        if save_path.exists():
            seen_links = orjson.loads(save_path.read_bytes())
        self.seen_links = seen_links

        if isinstance(hash_save_path, str):
            hash_save_path = Path(hash_save_path)
        self.hash_save_path = hash_save_path

        seen_hashes = dict()
        if hash_save_path.exists():
            seen_hashes = orjson.loads(hash_save_path.read_bytes())
        self.seen_hashes = seen_hashes

        if isinstance(description_hash_save_path, str):
            description_hash_save_path = Path(description_hash_save_path)
        self.description_hash_save_path = description_hash_save_path

        seen_description_hashes = dict()
        if description_hash_save_path.exists():
            seen_description_hashes = orjson.loads(description_hash_save_path.read_bytes())
        self.seen_description_hashes = seen_description_hashes

    def update(self, link):
        if link not in self.seen_links:
            self.seen_links[link] = 1
            self.save_path.write_bytes(orjson.dumps(self.seen_links))

    def update_hash(self, hash_):
        if hash_ not in self.seen_hashes:
            self.seen_hashes[hash_] = 1
            self.hash_save_path.write_bytes(orjson.dumps(self.seen_hashes))

    def contains_hash(self, hash_):
        return hash_ in self.seen_hashes

    def update_description_hash(self, hash_):
        if hash_ not in self.seen_description_hashes:
            self.seen_description_hashes[hash_] = 1
            self.description_hash_save_path.write_bytes(orjson.dumps(self.seen_description_hashes))

    def contains_description_hash(self, hash_):
        return hash_ in self.seen_description_hashes

    def __contains__(self, link):
        return link in self.seen_links
