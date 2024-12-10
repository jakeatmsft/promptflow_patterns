# Copyright (c) Microsoft. All rights reserved.

from semantic_kernel.functions import kernel_function, KernelParameterMetadata

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

class FinancePlugin:
    """
    A plugin to search Bing.
    """

    @kernel_function(
        description="Use yfinance to identify the latest ticker price",
        name="find_ticker_price",
        #input=[KernelParameterMetadata(name="limit", description="How many results to return", default_value="1",),
        #        KernelParameterMetadata(name="offset", description="How many results to skip", default_value="0")],
        #input_description="The topic to search, e.g. 'who won the F1 title in 2023?'",
    )

    async def find_ticker_price(self, ticker: str) -> str:
        """
        A native function that uses yfinance to find the latest ticker price.
        """

        # Download the historical stock data
        stock_data = yf.download(tickers=ticker, period="1d")
        
        # Get the latest price
        latest_price = stock_data["Close"].iloc[-1]
        return latest_price
