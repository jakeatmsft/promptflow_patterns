from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection
import os
import sys
import json

import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as skaoai
from semantic_kernel.planners.basic_planner import BasicPlanner
import APIPlugin.CustomAPIPlugin as customapi_plugin

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need


@tool
async def my_python_tool(ask: str,deployment:str, aoai_connection:AzureOpenAIConnection ) -> str:    
    kernel = sk.Kernel()
    service_id = None
    base_skills_directory = './plugins'
    kernel.add_service(skaoai.AzureChatCompletion(deployment_name=deployment,endpoint=aoai_connection.api_base,api_key=aoai_connection.api_key,api_version = "2023-12-01-preview"))
    planner = BasicPlanner(service_id)  
    
    custom_plugin = kernel.import_plugin_from_object(customapi_plugin.CustomAPIPlugin(), plugin_name="CustomAPI")  #.import_native_skill_from_directory(base_plugin , "APIPlugin")
    writer_plugin = kernel.import_plugin_from_prompt_directory(base_skills_directory, "WriterPlugin")
    email_plugin = kernel.import_plugin_from_prompt_directory(base_skills_directory, "EmailPlugin")
    translate_plugin = kernel.import_plugin_from_prompt_directory(base_skills_directory, "TranslatePlugin")

    plan = await planner.create_plan(ask, kernel)
    plan_out = str(plan.generated_plan)
    
    results = await planner.execute_plan(plan, kernel)
    
    return {"plan":plan_out, "result": results}