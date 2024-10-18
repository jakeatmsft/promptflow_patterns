import os

from dotenv import load_dotenv
from aiohttp import web
from ragtools import attach_rag_tools
from rtmt import RTMiddleTier
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential


if __name__ == "__main__":
    load_dotenv()
    llm_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    llm_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    print(f"llm_endpoint: {llm_endpoint}")
    print(f"llm_deployment: {llm_deployment}")


    credentials = DefaultAzureCredential() if not llm_key else None

    app = web.Application()

    rtmt = RTMiddleTier(llm_endpoint, llm_deployment, AzureKeyCredential(llm_key) if llm_key else credentials)
    rtmt.system_message = "You are a helpful assistant. Only answer questions based on information you have retrieved from the analyst tool. " + \
                          "The analyst tool can retrieve web information and provide analysis that you can use to answer questions. " + \
                          "For any question please use the analyst tool to look up the information. " + \
                          "The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. " + \
                          "Never read file names or source names or keys out loud. " + \
                          "Before using analyst tool, please ask the user to wait with the following phrase 'please wait while I look that up' while you look up the information. " + \
                          "Always use the following step-by-step instructions to respond: \n" + \
                          "1. When using the 'analyst' tool, always ask the user to wait with the following phrase 'please wait while I look that up' while you look up the information. \n" + \
                          "2. Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know."
    attach_rag_tools(rtmt, credentials)

    rtmt.attach_to_app(app, "/realtime")

    app.add_routes([web.get('/', lambda _: web.FileResponse('./static/index.html'))])
    app.router.add_static('/', path='./static', name='static')
    web.run_app(app, host='localhost', port=8765)
