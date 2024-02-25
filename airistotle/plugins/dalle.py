import openai
import json

from .base import BasePlugin


class Dalle(BasePlugin):
    """
    {
        "name": "dalle",
        "description": "Generates an image using the OpenAI Dalle 3 model. Uses the standard image generation via OpenAI API.",
        "parameters": {
            "type": "object",
            "properties": {
            "prompt": {
                "type": "string",
                "description": "A text description of the desired image(s). The maximum length is 4000 characters."
            },
            "size": {
                "type": "string",
                "description": "The size of the generated images. Must be one of 1024x1024, 1792x1024, or 1024x1792"
            },
            "style": {
                "type": "string",
                "description": "The style of the generated images. Must be one of 'vivid' or 'natural'. Vivid causes the model to lean towards generating hyper-real and dramatic images. Natural causes the model to produce more natural, less hyper-real looking images."
            }
            },
            "required": [
            "prompt"
            ]
        }
    }
    """
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
