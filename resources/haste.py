import requests

from resources.config import Config
from resources.errors import DocumentNotFound


class HasteDocument:
    @staticmethod
    def from_json(json):
        return HasteDocument(json["key"], json["data"])

    @staticmethod
    def get(key):
        response = requests.get(f"{Config.DOCUMENTS_PATH}/{key}")
        if response.status_code == 200:
            return HasteDocument.from_json(response.json())
        elif response.status_code == 404:
            raise DocumentNotFound()
        else:
            response.raise_for_status()

    @staticmethod
    def create(data):
        response = requests.post(Config.DOCUMENTS_PATH, data=data)
        if response.status_code == 200:
            if int(response.headers["X-RateLimit-Remaining"]) <= 10:
                print("Warning: Your rate limit is very long: You have less than 10 requests left!")
            return HasteDocument(response.json()["key"], data)
        else:
            response.raise_for_status()

    def __init__(self, key: str, data: str):
        self.key = key
        self.data = data
