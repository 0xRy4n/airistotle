# Built-ins
from typing import Optional as Opt

# Third Party
from haystack.nodes import WebRetriever, PromptNode
from haystack.pipelines import Pipeline
from haystack.nodes.search_engine.providers import GoogleAPI, SerperDev

# AIRISTOTLE
from .base import BasePlugin
from ..logger import GlobalLogger


class WebSearch(BasePlugin):
    """
    {
        "name": "web_search",
        "description": "Perform a web search and retrieve the contents from the top results. Use this when ever you are unsure of an answer and need more information. Use it to supplement your own knowledge, not replace it.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The query you want to search for."
            }
            },
            "required": [
            "query"
            ]
        }
    }
    """
    name = "web_search"
    description = "Searches the web for the query and returns the top results."

    def __init__(
        self,
        openai_api_key: Opt[str] = None,
        google_api_key: Opt[str] = None,
        google_cse_id: Opt[str] = None,
        serper_api_key: Opt[str] = None,
        prompt_node_model: Opt[str] = None,
        prompt_node_template: Opt[str] = None,
    ):
        """Initializes a WebSearch Plugin Function Object.

        ## Params:
            - open_api_key: The OpenAI API Key to use for the GPT-3 API.

            - google_api_key: The Google API Key to use for the Google API.
                                Not needed if using Serper API Key.
            - google_cse_id: The Google CSE ID to use for the Google API.
                                Not needed if using Serper API Key.
            - serper_api_key: The Serper API Key to use for the Serper API.
                                Can be specified instead of the Google API Key
                                and Google CSE ID.

            - prompt_node_model: The model to use for the Prompt Node (e.g. "gpt-3.5-turbo")
            - prompt_node_template: The template to use for the Prompt Node. Must be from https://prompthub.deepset.ai/
        """
        self.log = GlobalLogger("WebSearch")
        self.log.debug("Initializing WebSearch Plugin Function.")

        self.openai_api_key = openai_api_key
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.serper_api_key = serper_api_key
        self.prompt_node_model = prompt_node_model or "gpt-3.5-turbo-16k"
        self.prompt_node_template = prompt_node_template or "deepset/summarization"

        print([self.google_api_key and self.google_cse_id, self.serper_api_key])
        assert any(
            [self.google_api_key and self.google_cse_id, self.serper_api_key]
        ), "Must specify either Google API Key and Google CSE ID or Serper API Key."

        self.pipeline = self._setup_pipeline()

        self.log.audit(f"Using prompt model: {self.prompt_node_model}")

    def run(self, query: str) -> str:
        self.log.debug("Running WebSearch Plugin Function with query: {query}")

        result = self.pipeline.run(query=query) or {}
        summarized_results = str(result.get("results"))

        self.log.audit(f"WebSearch Plugin Function returned: {summarized_results}")
        return summarized_results

    def _setup_pipeline(self):
        api_key = self.google_api_key or self.serper_api_key or ""

        if self.google_api_key:
            self.log.debug("Using Google API for WebSearch Plugin Function.")
            search_engine = GoogleAPI(api_key=api_key, engine_id=self.google_cse_id)
        else:
            self.log.debug("Using Serper API for WebSearch Plugin Function.")
            search_engine = SerperDev(api_key=api_key)

        retriever = WebRetriever(
            api_key=api_key,
            search_engine_provider=search_engine,
            top_search_results=40,
            top_k=4,
            mode="preprocessed_documents",
        )

        prompt_node = PromptNode(
            self.prompt_node_model,
            api_key=self.openai_api_key,
            max_length=4000,
            default_prompt_template=self.prompt_node_template,
        )

        pipeline = Pipeline()
        pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
        pipeline.add_node(
            component=prompt_node, name="PromptNode", inputs=["Retriever"]
        )

        return pipeline
