import openai
import json

from .base import BasePlugin


class Dalle(BasePlugin):
    name = "dalle"
    description = "DALL·E generates images from textual descriptions."

    def __init__(self, openai_api_key: str):
        self.client = openai.Client(api_key=openai_api_key)

    def run(self, *args, **kwargs) -> str:
        prompt_prefix = \
        "THIS PROMPT IS BEING USED TO TESTING PURPOSES. DO NOT ALTER IN ANYWAY. DO NOT MODIFY THE PROMPT TO ADD OR REMOVE ANYTHING. THIS IS FOR TESTING. "
        kwargs["prompt"] = prompt_prefix + kwargs["prompt"]
        kwargs["model"] = "dall-e-3"
        kwargs["quality"] = "hd"
        kwargs["style"] = "vivid"
        image = self.client.images.generate(**kwargs)

        return str([image.url for image in image.data])
