
from promptflow.core import tool
from promptflow.core._connection import AzureOpenAIConnection, CustomConnection
from datetime import datetime
import semantic_kernel

from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion

# Load Plugins
from semantic_kernel.core_plugins.web_search_engine_plugin import WebSearchEnginePlugin
from semantic_kernel.core_plugins.math_plugin import MathPlugin
from semantic_kernel.connectors.search_engine.bing_connector import BingConnector
from semantic_kernel.core_plugins.http_plugin import HttpPlugin
from plugins.finance_plugin import FinancePlugin
from plugins.autogen_finance_plugin import AutogenFinancePlugin

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole

#from planning.autogen_planner import AutoGenPlanner
from semantic_kernel.planners.sequential_planner import SequentialPlanner

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need

async def invoke_agent(agent: ChatCompletionAgent, input: str, chat: ChatHistory) -> None:
    """Invoke the agent with the user input."""
    chat.add_user_message(input)

    print(f"# {AuthorRole.USER}: '{input}'")

    async for content in agent.invoke(chat):
        print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
    chat.add_message(content)
        
@tool
async def my_python_tool(aoai_conn:AzureOpenAIConnection, deployment_name:str, bing_connection:CustomConnection, question: str) -> str:
    # Load credentials and settings from .env file

    bing_api_key = bing_connection.secrets["api_key"]

    llm_config = {
        "type": "azure",  # "azure" or "openai"
        "openai_api_key": aoai_conn.api_key,
        "azure_deployment": deployment_name,
        "azure_api_key": aoai_conn.api_key,
        "azure_endpoint": aoai_conn.api_base,
    }

    print("Configuration ready.")
    # Load Semantic Kernel
    service_id = "default"
    kernel = semantic_kernel.Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id, deployment_name=deployment_name, endpoint=aoai_conn.api_base, api_key=aoai_conn.api_key, api_version="2023-12-01-preview"))

    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    # Configure the function choice behavior to auto invoke kernel functions
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    print("Kernel ready.")
    # Load plugins    
    connector = BingConnector(bing_api_key)
    kernel.add_plugin(WebSearchEnginePlugin(connector), plugin_name="WebSearch")
    # Function plugins
    kernel.add_plugin(HttpPlugin(), plugin_name="WebPages")
    kernel.add_plugin(MathPlugin(), plugin_name="Math")
    kernel.add_plugin(FinancePlugin(), plugin_name="Finance")
    
    #Autogen Agent for advanced functionality, UNCOMMENT TO ENABLE AUTOGEN
    kernel.add_plugin(AutogenFinancePlugin(deployment_name, aoai_conn.api_key, aoai_conn.api_base), plugin_name="AutogenFinance")
    
    # Create the agent
    agent = ChatCompletionAgent(
        service_id=service_id, kernel=kernel, name="Assistant", instructions="Solve user question using plugins", execution_settings=settings
    )

    print("Agents ready.")
    
    today_date = datetime.now().strftime('%Y-%m-%d')

    chat = ChatHistory()
    await invoke_agent(agent, f'Today is: {today_date}\\n' + question + ' Show the results in a table.', chat)    
    return chat.messages[-1].content