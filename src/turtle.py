import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from get_data import get_data

# define strategy
class Turtle(Strategy):

    sl,tp=0.1,0.1
    h,l=20,20

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]
        past_high = self.data.High[(-self.h-1):-1].max()
        past_low = self.data.Low[(-self.l-1):-1].min()
        if not self.position and current_high>past_high:
            self.buy(sl=current_close*(1-self.sl),tp=current_close*(1+self.tp))
        elif self.position and current_low<past_low:
            self.position.close()




# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,h,l,sl,tp,verbose=False):
        data=get_data(ticker, start_date="2019-01-01")
        class LocalTurtle(Turtle):
            pass
        LocalTurtle.h=h
        LocalTurtle.l=l
        LocalTurtle.sl=sl
        LocalTurtle.tp=tp
        bt=Backtest(data,LocalTurtle,cash=10000,
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
        get_data(ticker, start_date="2019-01-01") # force cache miss
        for h in [2,3,5,10,20]:
            for l in [2,3,5,10,20]:
                for sl in [0.05,0.1,0.15,0.2,0.25]:
                    for tp in [0.05,0.1,0.15,0.2,0.25]:
                        params.append([ticker,h,l,sl,sl])
    # execute simulations in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results=list(executor.map(lambda p: run(*p,verbose=False),params))
    # assemble results
    df=pd.DataFrame(params)
    df.columns=["ticker","h","l","sl","tp"]
    df["Calmar Ratio"]=list(map(lambda r:r["Calmar Ratio"],results))
    # report results
    df.to_csv(results_filename)
    df=df.groupby(["ticker","h","l","sl","tp"],as_index=False)["Calmar Ratio"].agg("mean")
    print("BEST PARAMS:")
    best=df.iloc[np.argmax(df["Calmar Ratio"].values),:]
    print(best)
    print("SAMPLE RUN OF BEST:")
    print(run(*best.tolist()[:5],verbose=False))
    print("FINAL SUMMARY:")
    print(df.sort_values("Calmar Ratio",ascending=False))

exp()





