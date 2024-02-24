import openai
import json

from .base import BasePlugin


class Dalle(BasePlugin):
    name = "dalle"
    description = "DALL·E generates images from textual descriptions."

    def __init__(self, openai_api_key: str):
        self.client = openai.Client(api_key=openai_api_key)

    def run(self, *args, **kwargs) -> str:
        image = self.client.images.generate(**kwargs)

        return str([image.url for image in image.data])
