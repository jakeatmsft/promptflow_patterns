from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection
import os
import sys
import json

import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as skaoai
from semantic_kernel.planners import SequentialPlanner
import APIPlugin.CustomAPIPlugin as customapi_plugin

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need


@tool
async def my_python_tool(ask: str,deployment:str, aoai_connection:AzureOpenAIConnection ) -> str:    
    kernel = sk.Kernel()
    service_id = "default"
    base_skills_directory = './plugins'
    kernel.add_service(skaoai.AzureChatCompletion(service_id=service_id, deployment_name=deployment,endpoint=aoai_connection.api_base,api_key=aoai_connection.api_key,api_version = "2023-12-01-preview"))
    planner = SequentialPlanner(kernel, service_id)  
    
    custom_plugin = kernel.add_plugin(customapi_plugin.CustomAPIPlugin(), plugin_name="CustomAPI")  #.import_native_skill_from_directory(base_plugin , "APIPlugin")
    writer_plugin = kernel.add_plugin(base_skills_directory, "WriterPlugin")
    email_plugin = kernel.add_plugin(base_skills_directory, "EmailPlugin")
    translate_plugin = kernel.add_plugin(base_skills_directory, "TranslatePlugin")

    plan = await planner.create_plan(ask)
    plan_out = str(plan.steps)
    
    results = await plan.invoke(kernel)
    
    return {'results': results.model_dump(mode='python')}