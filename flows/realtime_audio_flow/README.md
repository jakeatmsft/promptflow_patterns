# Voice Flow
Voice Flow is designed for conversational application development using audio inputs and outputs, leveraging the capabilities of the GPT-4o-Realtime-Preview model for voice-to-voice interactions. With Voice Flow, you can easily create a voicebot that handles audio input and generates both audio and text outputs.

## Prerequisites
```bash
pip install -r requirements.txt
pip install rtclient-0.5.1-py3-none-any.whl

## Create connection for LLM tool to use
You can follow these steps to create a connection required by a LLM tool.

Currently, there are two connection types supported by LLM tool: "AzureOpenAI" and "OpenAI". If you want to use "AzureOpenAI" connection type, you need to create an Azure OpenAI service first. Please refer to [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for more details. If you want to use "OpenAI" connection type, you need to create an OpenAI account first. Please refer to [OpenAI](https://platform.openai.com/) for more details.

```bash
# Override keys with --set to avoid yaml file changes
# Create open ai connection
pf connection create --file openai.yaml --set api_key=<your_api_key> --name open_ai_connection

# Create azure open ai connection
# pf connection create --file azure_openai.yaml --set api_key=<your_api_key> api_base=<your_api_base> --name open_ai_connection
```

Note in [flow.dag.yaml](flow.dag.yaml) we are using connection named `open_ai_connection`.
```bash
# show registered connection
pf connection show --name open_ai_connection
```
Please refer to connections [document](https://promptflow.azurewebsites.net/community/local/manage-connections.html) and [example](https://github.com/microsoft/promptflow/tree/main/examples/connections) for more details.

## Develop a voice flow

The most important elements that differentiate a voice flow from a standard flow are **Audio Input**, **Audio Output**, and **Text Output**.

- **Audio Input**: Audio input refers to the voice messages or queries submitted by users to the voicebot. Effectively handling audio input is crucial for a successful conversation, as it involves understanding user intentions, extracting relevant information, and triggering appropriate responses.

- **Audio Output**: Audio output refers to the AI-generated voice messages that are sent to the user in response to their inputs. Generating contextually appropriate and engaging audio outputs is vital for a positive user experience.

- **Text Output**: Text output refers to the AI-generated text that accompanies the audio output, providing a written record of the conversation.

A voice flow can have multiple inputs, but Audio Input is a required input in voice flow.

## Interact with voice flow

Promptflow CLI provides a way to start an interactive voice session for voice flow. Customers can use the below command to start an interactive voice session:
