import openai

from .base import BasePlugin



class Dalle(BasePlugin):
    name = "dalle"
    description = "DALL·E is a 12-billion parameter version of GPT-3. It is trained to generate images from textual descriptions."

    def __init__(self, openai_api_key: str):
        self.client = openai.Client(api_key=openai_api_key)

    def run(self, *args, **kwargs) -> str:
        image = self.client.images.generate(
            model="dall-e-3",
            prompt=kwargs.get("prompt"),
            quality=kwargs.get("quality"),
            response_format="url",
            size=kwargs.get("size"),
            style=kwargs.get("style")
        )

        return image.url
