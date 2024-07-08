
from promptflow.core import tool
import io
import bs4
import pandas as pd


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(fileinput1: str) -> str:
    with open(fileinput1,'r') as f:
        content = f.read()
        soup = bs4.BeautifulSoup(content, 'html.parser')
        table = soup.find('p',{'id':'INCOME_STATEMENTS'}).findNext('table')
        table_txt = ''
        for td in table:
            if td.text:
                table_txt+=(td.text)
                
        return table_txt