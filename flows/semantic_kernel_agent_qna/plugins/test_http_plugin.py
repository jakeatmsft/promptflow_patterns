import asyncio
from http_plugin import HttpBrowsePlugin
from datetime import datetime


async def main():
    plugin = HttpBrowsePlugin()

    urls = [
        'https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/model-retirements',
    ]

    for url in urls:
        try:
            print(f"Fetching URL: {url}")
            result = await plugin.get(url)
            print(f"Result for {url}:\n{result}...\n") 
            print(f"result_chars: {len(result)}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'results_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(result)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

if __name__ == '__main__':
    asyncio.run(main())