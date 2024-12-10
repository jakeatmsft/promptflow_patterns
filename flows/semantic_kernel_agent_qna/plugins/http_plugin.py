import json
import re
from typing import Annotated, Any, Optional, Dict

import aiohttp
from bs4 import BeautifulSoup
from readability import Document

from semantic_kernel.exceptions import FunctionExecutionException
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
def is_probably_readable(soup: BeautifulSoup, min_score: int = 100) -> bool:
    # Implement a function to check if the document is probably readable
    # This is a placeholder implementation
    return True

async def readable_text(params: Dict[str, Any]) -> Optional[str]:
    html = params['html']
    url = params['url']
    settings = params['settings']
    options = params.get('options', {})

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Check if the document is probably readable
    if options.get('fallback_to_none') and not is_probably_readable(soup):
        return html

    # Use readability to parse the document
    doc = Document(html)
    parsed = doc.summary()
    parsed_title = doc.title()

    # Create a new BeautifulSoup object for the parsed content
    readability_soup = BeautifulSoup(parsed, 'html.parser')

    # Insert the title at the beginning of the content
    if parsed_title:
        title_element = readability_soup.new_tag('h1')
        title_element.string = parsed_title
        readability_soup.insert(0, title_element)

    return str(readability_soup)

async def process_html(html: str, url: str, settings: dict, soup: BeautifulSoup) -> str:
        body = soup.body
        if 'remove_elements_css_selector' in settings:
            for element in body.select(settings['remove_elements_css_selector']):
                element.decompose()
        
        simplified_body = body.decode_contents().strip()

        if isinstance(simplified_body, str):
            simplified = f"""<html lang="">
            <head>
                <title>
                    {soup.title.string if soup.title else ''}
                </title>
            </head>
            <body>
                {simplified_body}
            </body>
        </html>"""
        else:
            simplified = html or ''

        ret = None
        if settings.get('html_transformer') == 'readableText':
            try:
                ret = await readable_text({'html': simplified, 'url': url, 'settings': settings, 'options': {'fallback_to_none': False}})
            except Exception as error:
                print(f"Processing of HTML failed with error: {error}")

        return ret or simplified


class HttpBrowsePlugin(KernelBaseModel):
    """A plugin that provides HTTP functionality.
    
    Usage:
        kernel.add_plugin(HttpPlugin(), "http")

    Examples:
        {{http.getAsync $url}}
        {{http.postAsync $url}}
    """   

    @kernel_function(description="Makes a GET request to a url", name="getAsync")
    async def get(self, url: Annotated[str, "The URL to send the request to."]) -> str:
        """Sends an HTTP GET request to the specified URI and returns the response body as a string.

        Args:
            url: The URL to send the request to.

        Returns:
            The response body as a string.
        """
        if not url:
            raise FunctionExecutionException("url cannot be `None` or empty")

        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, raise_for_status=True) as response:
                response_text = await response.text()
                result = await process_html(response_text,  url, {'html_transformer': 'readableText','readableTextCharThreshold': 500}, BeautifulSoup(response_text, 'html.parser'))
                return result

    @kernel_function(description="Makes a POST request to a uri", name="postAsync")
    async def post(
        self,
        url: Annotated[str, "The URI to send the request to."],
        body: Annotated[dict[str, Any] | None, "The body of the request"] = {},
    ) -> str:
        """Sends an HTTP POST request to the specified URI and returns the response body as a string.

        Args:
            url: The URI to send the request to.
            body: Contains the body of the request.

        Returns:
            The response body as a string.
        """
        if not url:
            raise FunctionExecutionException("url cannot be `None` or empty")

        headers = {"Content-Type": "application/json"}
        data = json.dumps(body)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, raise_for_status=True) as response:
                response_text = await response.text()
                # List of tags to remove
                tags_to_remove = ["meta", "script"]
                # Create regex pattern from the list of tags
                pattern = r'<({})[^>]*>.*?</\1>'.format("|".join(tags_to_remove))
                # Remove the specified tags and their content
                cleaned_text = re.sub(pattern, '', response_text, flags=re.DOTALL)
                return cleaned_text[:2000]

