from semantic_kernel.functions import kernel_function

'''
Function descriptions:
Planner - An expert in breaking down a problem into an executable plan.
WebSearcher - A web searcher with access to an external live web index.
MarketAnalyst - An experienced financial analyst familiar with all types of valuation methods using market data (not analyst projections). No access to up to date data and cannot perform calculations.
VizLoader - Loads pre-existing vizlets from fcodes which refer to vizlets (not data). Only use this if asked explicitly to load the vizlet at a specific fcode. This is mutually exclusive with VizletBuilder.
VizBuilder - Creates vizlets from scratch. Provide the vizlet builder the relevant data reference ids. This is mutually exclusive with vizlet_loader.
Coder - Writes code and uses the provided python repl tool to execute. Do not call me without telling me the specific fcode values which you want me to operate on and the descriptions of them as provided by the DataFinder.
DataFinder - Takes economic concepts and identifies the correct fcode (a unique identifier) for the data which represents that concept. Or if no data is found, suggests a suitable proxy including a possible formula for deriving the proxy. If a proxy formula is specified, make sure that you give that information to the Coder. This worker takes multiple concepts in one shot and returns all of the fcodes. Do not create a plan where this work is called once per concept. This worker should only be called once in the plan. This worker should still be called even if the user provides explicit fcodes; simply say 'Please load the fcode xxx'. This worker will provide metadata for each found and loaded concept such as description (for Coder) and label (for VizletBuilder).
'''
class CustomAPIPlugin:
    """
    Description: api plugin for planner
    """
    @kernel_function(
        description = "Get news from the web",
        name = "NewsPlugin",
    )
    def get_news_api(self,location:str) -> str:
        return """Get news from the """ + location + """."""
    
    @kernel_function(
            description="Search Weather in a city",
            name="WeatherFunction",
        )
    def ask_weather_function(self,city: str) -> str:
        return city + "’s weather is 30 celsius degree , and very hot."
    
    @kernel_function(
            description="Search Docs",
            name="DocsFunction",
        )
    def ask_docs_function(self,docs: str) -> str:
        return "ask docs :" + docs

    @kernel_function(
        description="WebSearcher - A web searcher with access to an external live web index.",
        name="WebSearchFunction",
    )
    def web_search_function(self, query: str) -> str:
        # Implementation of the web search function goes here
        return  "Calling WebSearchFunction with query: " + query

    @kernel_function(
        description="MarketAnalyst - An experienced financial analyst familiar with all types of valuation methods using market data.",
        name="MarketAnalystFunction",
    )
    def market_analyst_function(self, market_data: str) -> str:
        # Implementation of the market analyst function goes here
        return "Calling MarketAnalystFunction with market data: " + market_data

    @kernel_function(
        description="VizLoader - Loads pre-existing visuals from library.",
        name="VizLoaderFunction",
    )
    def viz_loader_function(self, fcode: str) -> str:
        # Implementation of the vizlet loader function goes here
        return "Calling VizLoaderFunction with fcode: " + fcode

    @kernel_function(
        description="VizBuilder - Creates visuals from scratch.",
        name="VizBuilderFunction",
    )
    def viz_builder_function(self, data_reference_ids: str) -> str:
        # Implementation of the vizlet builder function goes here
        return "Calling VizBuilderFunction with data reference ids: " + data_reference_ids

    @kernel_function(
        description="Coder - Writes code and uses the provided python repl tool to execute.",
        name="CoderFunction",
    )
    def coder_function(self, fcode_values: str, descriptions: str) -> str:
        # Implementation of the coder function goes here
        return "Calling CoderFunction with fcode values: " + fcode_values + " and descriptions: " + descriptions

    @kernel_function(
        description="DataFinder - Takes economic concepts and identifies the correct fcode.",
        name="DataFinderFunction",
    )
    def data_finder_function(self, concepts: str) -> str:
        # Implementation of the data finder function goes here
        return "Calling DataFinderFunction with concepts: " + concepts
    
    