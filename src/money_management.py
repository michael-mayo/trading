import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from get_data import get_data

# define strategy
class MoneyManagement(Strategy):

    ma=200
    sl,tp=0.1,0.1

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        if not self.position and np.random.random()>=0.5:
            c=self.data.Close[-1]
            if self.ma<=0 or c>self.data.Close[-self.ma:].mean():
                self.buy(sl=c-c*self.sl,tp=c+c*self.tp)




# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,sl,tp,ma,verbose=False):
        data=get_data(ticker, start_date="2019-01-01")
        MoneyManagement.sl=sl
        MoneyManagement.tp=tp
        MoneyManagement.ma=ma
        bt=Backtest(data,MoneyManagement,cash=10000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False)
        stats=bt.run()
        if verbose:
            print(ticker)
            print(stats)
            print(stats._trades)
            bt.plot()
        return stats

# do an experiment
def exp(results_filename="results.csv"):
    # build param sets; 1000 iterations per param set is recommended for precision
    params=[]
    for ticker in ["TQQQ"]:
        for sl in [0.05,0.1,0.2]:
            for tp in [0.05,0.1,0.2]:
                for ma in [0,5,10,20,50,100,200]:
                    for _ in range(1000):
                        params.append([ticker,sl,tp,ma])
    # execute simulations in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results=list(executor.map(lambda p: run(*p,verbose=False),params))
    # assemble results
    df=pd.DataFrame(params)
    df.columns=["ticker","sl","tp","ma"]
    df["Calmar Ratio"]=list(map(lambda r:r["Calmar Ratio"],results))
    # report results
    df.to_csv(results_filename)
    df=df.groupby(["ticker","sl","tp","ma"],as_index=False)["Calmar Ratio"].agg("mean")
    print("BEST PARAMS:")
    best=df.iloc[np.argmax(df["Calmar Ratio"].values),:]
    print(best)
    print("SAMPLE RUN OF BEST:")
    print(run(*best.tolist()[:4],verbose=False))
    print("FINAL SUMMARY:")
    print(df.sort_values("Calmar Ratio",ascending=False))

exp()





