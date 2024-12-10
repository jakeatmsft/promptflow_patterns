# Assistant Chat flow for agentic Question and Answering specific domain
This template also includes multi-agent tools specifically designed for question and answer tasks. These tools can help automate various operations, such as information retrieval, context management, and response generation. By integrating these tools into your chat flow, you can create a powerful assistant capable of handling complex queries and tasks across multiple domains.

## Create connection for LLM tool to use
You can follow these steps to create a connection required by a LLM tool.

Currently, there are two connection types supported by LLM tool: "AzureOpenAI" and "OpenAI". If you want to use "AzureOpenAI" connection type, you need to create an Azure OpenAI service first. Please refer to [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for more details. If you want to use "OpenAI" connection type, you need to create an OpenAI account first. Please refer to [OpenAI](https://platform.openai.com/) for more details.

```bash
# create bing api connection
pf connection create --file bing_connection.yaml 

# Create azure open ai connection
 pf connection create --file default_azureopenai.yaml 
```
Please refer to connections [document](https://promptflow.azurewebsites.net/community/local/manage-connections.html) and [example](https://github.com/microsoft/promptflow/tree/main/examples/connections) for more details.

## Develop a chat flow

The most important elements that differentiate a chat flow from a standard flow are **Chat Input**, **Chat History**, and **Chat Output**.

- **Chat Input**: Chat input refers to the messages or queries submitted by users to the chatbot. Effectively handling chat input is crucial for a successful conversation, as it involves understanding user intentions, extracting relevant information, and triggering appropriate responses.

- **Chat History**: Chat history is the record of all interactions between the user and the chatbot, including both user inputs and AI-generated outputs. Maintaining chat history is essential for keeping track of the conversation context and ensuring the AI can generate contextually relevant responses. Chat History is a special type of chat flow input, that stores chat messages in a structured format.

- **Chat Output**: Chat output refers to the AI-generated messages that are sent to the user in response to their inputs. Generating contextually appropriate and engaging chat outputs is vital for a positive user experience.

A chat flow can have multiple inputs, but Chat History and Chat Input are required inputs in chat flow.

## Interact with chat flow

Promptflow CLI provides a way to start an interactive chat session for chat flow. Customer can use below command to start an interactive chat session:

```
pf flow test --flow <flow_folder> --interactive
```