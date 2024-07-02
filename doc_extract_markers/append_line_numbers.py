from promptflow.core import tool

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(input1: str) -> str:
    # Split the content into lines
    lines = input1.split('\n')
    # Prepend line numbers
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    # Join the modified lines back into a single string
    numbered_content = '\n'.join(numbered_lines)
    return(numbered_content)