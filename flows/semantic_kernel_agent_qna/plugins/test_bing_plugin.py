import asyncio
from bing_plugin import WebSearchEngineBingPlugin, NewBingConnector
from datetime import datetime


async def main():
    connector = NewBingConnector('bing_search_api_key')

    plugin = WebSearchEngineBingPlugin(connector)
    
    search = 'what is semantic kernel?'
    try:
        result = await plugin.search(query=search)
        print(f"Result for {search}:\n{result}...\n")
    except Exception as e:
        print(f"Failed to fetch {search}: {e}")

if __name__ == '__main__':
    asyncio.run(main())