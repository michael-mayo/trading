import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from get_data import get_data

# define strategy
class MoneyManagement(Strategy):

    sl=0.05
    p=200

    stop=None

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        if not self.position and (self.p==0 or self.data.Close[-1]>self.data.Close[-self.p:].mean()):
            self.buy()
            self.stop=self.data.Close[-1]*(1-self.sl)
        elif self.position and self.data.Close[-1]<=self.stop:
            self.position.close()
        elif self.position:
            self.stop=max(self.stop,self.data.Close[-1]*(1-self.sl))




# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,sl,p,verbose=False):
        data=get_data(ticker, start_date="2019-01-01")
        class LocalMoneyManagement(MoneyManagement):
            pass
        LocalMoneyManagement.sl=sl
        LocalMoneyManagement.p=p
        bt=Backtest(data,LocalMoneyManagement,cash=10000,
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
        get_data(ticker, start_date="2019-01-01")
        for sl in [0.05,0.1,0.15,0.2,0.25,0.3,0.35]:
            for p in [0,5,10,20,50,100,200]:
                params.append([ticker,sl,p])
    # execute simulations in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results=list(executor.map(lambda p: run(*p,verbose=False),params))
    # assemble results
    df=pd.DataFrame(params)
    df.columns=["ticker","sl","p"]
    df["Calmar Ratio"]=list(map(lambda r:r["Calmar Ratio"],results))
    # report results
    df.to_csv(results_filename)
    df=df.groupby(["ticker","sl","p"],as_index=False)["Calmar Ratio"].agg("mean")
    print("BEST PARAMS:")
    best=df.iloc[np.argmax(df["Calmar Ratio"].values),:]
    print(best)
    print("SAMPLE RUN OF BEST:")
    print(run(*best.tolist()[:3],verbose=True))
    print("FINAL SUMMARY:")
    print(df.sort_values("Calmar Ratio",ascending=False))

exp()





