
from promptflow.core import tool
import subprocess
import re


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
# def execute_code(program: str) -> str:
#     program = program.replace('```python', '')
#     program = program.replace('```', '')
#     program = program + '\\nprint(df.to_json)'
#     program = program.replace('\\n', '\n')
#     result = subprocess.run(['python', '-c', program], capture_output=True)
#     ans =str(result.stdout)
#     return ans


# import subprocess
# import json

def execute_code(program: str) -> str:
    # Remove Python code block markers
    program = program.replace('```python', '').replace('```', '')
    program = re.sub(r'^print\(.*\)\n?', '', program, flags=re.MULTILINE)
    
    # Append the print statement correctly to call df.to_json() method
    program += '\nprint(df.to_json())'
    
    # Execute the modified program string using subprocess
    result = subprocess.run(['python', '-c', program], capture_output=True, text=True)
    
    # Decode the output from bytes to string, if necessary, and return
    # Note: 'text=True' in subprocess.run() automatically decodes the output
    return result.stdout

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(input_program: str) -> str:
  result = execute_code(input_program)
  return result
