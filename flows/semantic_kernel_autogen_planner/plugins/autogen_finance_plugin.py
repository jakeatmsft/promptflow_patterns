# Copyright (c) Microsoft. All rights reserved.

from typing import Annotated
from semantic_kernel.functions import kernel_function, KernelParameterMetadata

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import autogen

class AutogenFinancePlugin:
    """
    A plugin to perform advanced finance tasks.
    """
    _config_list: list
    
    def __init__(self, deployment_name: str, api_key: str, base_url: str):
        self._config_list = [
                    {
                        "model": deployment_name,
                        "api_key": api_key,
                        "base_url": base_url,
                        "api_type": "azure",
                        "api_version": "2023-07-01-preview"
                    },
                    ]

    @kernel_function(
        description="Use autogen finance agent to solve the following task, use for tasks such as MACD, RSI, etc.",
        name="generate_finance_results",
    )

    async def generate_finance_results(self, question: Annotated[str, "Question requiring advanced finance operations"]) -> str:
        # create an AssistantAgent named "assistant"
        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={
                "cache_seed": None,  # disable
                "seed": None,  # disable
                "config_list": self._config_list,  # a list of OpenAI API configurations
                "temperature": 0,  # temperature for sampling
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )
        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,  # set to True or image name like "python:3" to use docker
            },
        )
        # the assistant receives a message from the user_proxy, which contains the task description
        user_proxy.initiate_chat(
            assistant,
            message=f"""Answer the following: {question}""",
        )

        output = assistant.last_message(agent=user_proxy)['content']
        return output