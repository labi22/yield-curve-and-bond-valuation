import pandas as pd
from pandas_datareader import data as pdr
from datetime import datetime


TREASURY_TICKERS = {
    "1M": "DGS1MO",
    "3M": "DGS3MO",
    "6M": "DGS6MO",
    "1Y": "DGS1",
    "2Y": "DGS2",
    "5Y": "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30"
}


def load_treasury_yields(start="2018-01-01", end=None):
    """
    Load US Treasury Constant Maturity yields from FRED.

    Returns:
        DataFrame indexed by date, columns as maturities (in years)
    """
    if end is None:
        end = datetime.today()

    df = pd.DataFrame()

    for label, ticker in TREASURY_TICKERS.items():
        df[label] = pdr.DataReader(ticker, "fred", start, end)

    # Convert % yields to decimals
    df = df / 100.0

    # Drop rows with missing values
    df = df.dropna()

    return df