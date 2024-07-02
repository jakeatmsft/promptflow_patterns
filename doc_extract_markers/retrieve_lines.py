from promptflow.core import tool
import json

@tool
def my_python_tool(lines: str, source: str) -> str:
    ret = ''
    # Split the content into lines
    src_lines = source.split('\n')
    # expected format {"lines":[{"start":line_start, "end":line_end}]}
    js_lines = json.loads(lines)

    for line in js_lines['lines']:
        # Join the lines selected and add them to the ret string
        selected_lines = '\n'.join(src_lines[line['start']:line['end']+1])
        ret += f'{line} : {selected_lines}\n'

    return ret