import os
import sys
import time
from datetime import datetime,timedelta
import yfinance as yf
import pandas as pd

def get_data(ticker: str,
             start_date: str = (datetime.today()
                                - timedelta(weeks=52 * 5)).strftime("%Y-%m-%d"),
             end_date: str = (datetime.today()
                              + timedelta(days=1)).strftime("%Y-%m-%d"),
             ) -> pd.DataFrame:
    key = f"{ticker}_{end_date}_{start_date}"
    path = f"/data/{key}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0)
    else:
        df = yf.download(tickers=ticker,
                         start=start_date, end=end_date,
                         auto_adjust=True).sort_index()
        df.columns = map(lambda t: t[0], list(df.columns))
        if df is not None and len(df)>0:
            df.to_csv(path)
        time.sleep(1)
    df.index = pd.to_datetime(df.index)
    return df

if __name__=="__main__":
    if len(sys.argv)<2:
        print("usage: python get_data.py <ticker> [<YYYY-MM-DD> <YYYY-MM-DD>]")
        exit()
    if len(sys.argv)==2:
        df=get_data(sys.argv[1])
    else:
        df=get_data(sys.argv[1],start_date=sys.argv[2],end_date=sys.argv[3])
    if df is None or len(df)==0:
        print("get_data.py failed")
    else:
        print(f"get_data.py succeeded, obtained {len(df)} records")