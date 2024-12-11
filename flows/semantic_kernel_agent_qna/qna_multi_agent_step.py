from datetime import datetime

from promptflow.core import tool
from promptflow.core._connection import AzureOpenAIConnection, CustomConnection

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.core_plugins.math_plugin import MathPlugin
from semantic_kernel.exceptions import FunctionExecutionException
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel
from semantic_kernel.planners.sequential_planner import SequentialPlanner
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy

# Using custom plugins
from plugins.bing_plugin import WebSearchEngineBingPlugin, NewBingConnector
from plugins.http_plugin import HttpBrowsePlugin

#import agentops


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
    
    #agentops.init("4d130bd9-")

    bing_api_key = bing_connection.secrets["api_key"]

    print("Configuration ready.")
    # Load Semantic Kernel
    service_id = "default"
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        service_id=service_id, 
        deployment_name=deployment_name, 
        endpoint=aoai_conn.api_base, 
        api_key=aoai_conn.api_key)
        )


    # Load plugins    
    connector = NewBingConnector(bing_api_key)
    kernel.add_plugin(WebSearchEngineBingPlugin(connector), plugin_name="WebSearch")
    # Function plugins
    kernel.add_plugin(HttpBrowsePlugin(), plugin_name="WebPages")
    kernel.add_plugin(MathPlugin(), plugin_name="Math")
    

    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    # Configure the function choice behavior to auto invoke kernel functions
    settings.function_choice_behavior = FunctionChoiceBehavior.Required()
    
    CharacterLimit = 2000
    Context = subject_context
    
    DOCS_QUESTION_ANSWER_NAME = "DocsQuestionAnswer"
    DOCS_QUESTION_ANSWER_INSTRUCTIONS = f"""
            You are a question answerer for {Context} using documentation site.  Use the WebSearch tool to retrieve information to answer the questions from the docs site.
            Prepend "site:learn.microsoft.com" to any search query to search only the documentation site. 
            You take in questions from a questionnaire and emit the answers from the perspective of {Context},
            using documentation from the public web. You also emit links to any websites you find that help answer the questions.
            Do not address the user as 'you' - make all responses solely in the third person.
            If you do not find information on a topic, you simply respond that there is no information available on that topic.
            You will emit an answer that is no greater than {CharacterLimit} characters in length.
        """
    ANSWER_CHECKER_NAME = "AnswerChecker"
    ANSWER_CHECKER_INSTRUCTIONS = f"""
            You are an answer checker for {Context}. Your responses always start with either the words ANSWER CORRECT or ANSWER INCORRECT.
            Given a question and an answer, you check the answer for accuracy regarding {Context},
            using public web sources when necessary. If everything in the answer is true, you verify the answer by responding "ANSWER CORRECT." with no further explanation.
            You also ensure that the answer is no greater than {CharacterLimit} characters in length.
            Otherwise, you respond "ANSWER INCORRECT - " and add the portion that is incorrect.
            You do not output anything other than "ANSWER CORRECT" or "ANSWER INCORRECT - <portion>".
        """
    LINK_CHECKER_NAME = "LinkChecker"
    LINK_CHECKER_INSTRUCTIONS = """
            You are a link checker. Your responses always start with either the words LINKS CORRECT or LINK INCORRECT.
            Given a question and an answer that contains links, you verify that the links are working and return a non-error response,
            using public web sources when necessary. If all links are working, you verify the answer by responding "LINKS CORRECT" with no further explanation.
            Otherwise, for each bad link, you respond "LINK INCORRECT - " and add the link that is incorrect.
            You do not output anything other than "LINKS CORRECT" or "LINK INCORRECT - <link>".
        """
    MANAGER_NAME = "Manager"
    MANAGER_INSTRUCTIONS = """
            You are a manager which reviews the question, the answer to the question, and the links.
            If the answer checker replies "ANSWER INCORRECT", or the link checker replies "LINK INCORRECT," you can reply "reject" and ask the question answerer to correct the answer.
            Once the question has been answered properly, you can approve the request by just responding "approve".
            You do not output anything other than "reject" or "approve".
        """

    
    docs_agent_question_answer = ChatCompletionAgent(
        service_id=service_id,
        kernel=kernel,
        name=DOCS_QUESTION_ANSWER_NAME,
        instructions=DOCS_QUESTION_ANSWER_INSTRUCTIONS,
        execution_settings=settings,

    )
    agent_answer_checker = ChatCompletionAgent(
        service_id=service_id,
        kernel=kernel,
        name=ANSWER_CHECKER_NAME,
        instructions=ANSWER_CHECKER_INSTRUCTIONS,
        execution_settings=settings,
    )
    agent_link_checker = ChatCompletionAgent(
        service_id=service_id,
        kernel=kernel,
        name=LINK_CHECKER_NAME,
        instructions=LINK_CHECKER_INSTRUCTIONS,
        execution_settings=settings,

    )
    agent_manager = ChatCompletionAgent(
        service_id=service_id,
        kernel=kernel,
        name=MANAGER_NAME,
        instructions=MANAGER_INSTRUCTIONS,
    )

    chat = AgentGroupChat(
        agents=[agent_answer_checker, docs_agent_question_answer, agent_link_checker, agent_manager],
        termination_strategy=ApprovalTerminationStrategy(agents=[agent_manager], maximum_iterations=10),
    )

    await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=question))
    print(f"# {AuthorRole.USER}: '{question}'")
    

    async for content in chat.invoke():
        print(f"# {content.role} - {content.name or '*'}: '{content.content}'")

    print(f"# IS COMPLETE: {chat.is_complete}")

    answer = None
    manager_response = None
    
    for message in reversed(chat.history):
        if message.name == MANAGER_NAME and manager_response is None:
            manager_response = message.content
        if message.name == DOCS_QUESTION_ANSWER_NAME and answer is None:
            answer = message.content
        if manager_response and answer:
            break
        
    #agentops.end_session('Success')

    return {"MANAGER_NAME": manager_response, "QUESTION_ANSWER_NAME": answer, "is_complete": chat.is_complete}

