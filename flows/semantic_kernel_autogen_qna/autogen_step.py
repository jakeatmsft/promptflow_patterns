
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

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole

#from planning.autogen_planner import AutoGenPlanner
from semantic_kernel.planners.sequential_planner import SequentialPlanner

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need

class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        if isinstance(history, list) and history:
            return any(keyword in history[-1].content.lower() for keyword in ["approve", "approved"])        
        return False
        
@tool
async def my_python_tool(aoai_conn:AzureOpenAIConnection, deployment_name:str, bing_connection:CustomConnection, subject_context:str, question: str) -> str:
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
    #kernel.add_plugin(AutogenFinancePlugin(deployment_name, aoai_conn.api_key, aoai_conn.api_base), plugin_name="AutogenFinance")
    CharacterLimit = 2000
    Context = subject_context
    
    QuestionAnswererPrompt = f"""
            You are a question answerer for {Context}.
            You take in questions from a questionnaire and emit the answers from the perspective of {Context},
            using documentation from the public web. You also emit links to any websites you find that help answer the questions.
            Do not address the user as 'you' - make all responses solely in the third person.
            If you do not find information on a topic, you simply respond that there is no information available on that topic.
            You will emit an answer that is no greater than {CharacterLimit} characters in length.
        """
    
    AnswerCheckerPrompt = f"""
            You are an answer checker for {Context}. Your responses always start with either the words ANSWER CORRECT or ANSWER INCORRECT.
            Given a question and an answer, you check the answer for accuracy regarding {Context},
            using public web sources when necessary. If everything in the answer is true, you verify the answer by responding "ANSWER CORRECT." with no further explanation.
            You also ensure that the answer is no greater than {CharacterLimit} characters in length.
            Otherwise, you respond "ANSWER INCORRECT - " and add the portion that is incorrect.
            You do not output anything other than "ANSWER CORRECT" or "ANSWER INCORRECT - <portion>".
        """
    
    LinkCheckerPrompt = """
            You are a link checker. Your responses always start with either the words LINKS CORRECT or LINK INCORRECT.
            Given a question and an answer that contains links, you verify that the links are working,
            using public web sources when necessary. If all links are working, you verify the answer by responding "LINKS CORRECT" with no further explanation.
            Otherwise, for each bad link, you respond "LINK INCORRECT - " and add the link that is incorrect.
            You do not output anything other than "LINKS CORRECT" or "LINK INCORRECT - <link>".
        """
    
    ManagerPrompt = """
            You are a manager which reviews the question, the answer to the question, and the links.
            If the answer checker replies "ANSWER INCORRECT", or the link checker replies "LINK INCORRECT," you can reply "reject" and ask the question answerer to correct the answer.
            Once the question has been answered properly, you can approve the request by just responding "approve".
            You do not output anything other than "reject" or "approve".
        """
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


    QuestionAnswererAgent = ChatCompletionAgent(service_id=service_id, kernel=kernel, name='QuestionAnswererAgent', instructions=QuestionAnswererPrompt, execution_settings=settings )
    AnswerCheckerAgent = ChatCompletionAgent(service_id=service_id, kernel=kernel, name='AnswerCheckerAgent', instructions=AnswerCheckerPrompt, execution_settings=settings )
    LinkCheckerAgent = ChatCompletionAgent(service_id=service_id, kernel=kernel, name='LinkCheckerAgent', instructions=LinkCheckerPrompt, execution_settings=settings )
    ManagerAgent = ChatCompletionAgent(service_id=service_id, kernel=kernel, name='ManagerAgent', instructions=ManagerPrompt)
    

    # Create the agent
    # agent = ChatCompletionAgent(
    #     service_id=service_id, kernel=kernel, name="Assistant", instructions="Solve user question using plugins", execution_settings=settings
    # )
    
    
    # Create the group chat
    chat = AgentGroupChat(
        agents=[QuestionAnswererAgent, AnswerCheckerAgent, LinkCheckerAgent, ManagerAgent],
        termination_strategy=ApprovalTerminationStrategy(agents=[ManagerAgent], maximum_iterations=25),
    )


    print("Agents ready.")
    
    today_date = datetime.now().strftime('%Y-%m-%d')

    await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=f'In the {Context}, {question}'))    
    print(f"# {AuthorRole.USER}: '{question}'")
    
    try:
        async for response in chat.invoke():
            print(f"# {response.role}: {response.content}")
            if chat.is_complete:
                break
    except Exception as e:
        print(f"An error occurred during chat invocation: {e}")

    print(f"# IS COMPLETE: {chat.is_complete}")

    return chat.history[-1].content