# Copyright (c) Microsoft. All rights reserved.

from semantic_kernel.functions import kernel_function, KernelParameterMetadata
from plugins.bing_connector import BingConnector


class BingPlugin:
    """
    A plugin to search Bing.
    """

    def __init__(self, bing_api_key: str):
        self.bing = BingConnector(api_key=bing_api_key)
        if not bing_api_key or bing_api_key == "...":
            raise Exception("Bing API key is not set")

    @kernel_function(
        description="Use Bing to find a page about a topic. The return is a URL of the page found",
        name="find_web_page_about",
        #input=[KernelParameterMetadata(name="limit", description="How many results to return", default_value="1",),
        #        KernelParameterMetadata(name="offset", description="How many results to skip", default_value="0")],
        #input_description="The topic to search, e.g. 'who won the F1 title in 2023?'",
    )

    async def find_web_page_about(self, input: str) -> str:
        """
        A native function that uses Bing to find a page URL about a topic.
        """
        result = await self.bing.search_url_async(
            query=input,
            num_results=1,
            offset=0,
        )
        if result:
            return result[0]
        else:
            return f"Nothing found, try again or try to adjust the topic."
