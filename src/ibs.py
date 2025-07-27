import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy

from get_data import get_data

# define strategy
class IBS(Strategy):

    t=0.9

    # constructor does nothing for now
    def init(self):
        self.num_bars=len(self.data.Close)

    # strategy actions for next day
    def next(self):
        o,h,l,c=self.data.Open[-1],self.data.High[-1],self.data.Low[-1],self.data.Close[-1]
        ibs=(c-l)/(h-l)
        if not self.position:
            self.buy()
        elif self.position and ibs>=self.t or len(self.data.Close)==self.num_bars:
            self.position.close()



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,t,verbose=False):
        data=get_data(ticker, start_date="2019-01-01").copy()
        IBS.t=t
        bt=Backtest(data,IBS,cash=10000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False)
        stats=bt.run()
        if verbose:
            print(ticker,t)
            print(stats)
            print(stats._trades)
            bt.plot()
        return stats





print("running grid search...")
results={}
best_params=None
best_score=None
for ticker in ["TQQQ"]:
    for t in [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
        params=(ticker,t)
        results[params]=run(*params)
        score=results[params]["CAGR [%]"]
        if best_score is None or score>best_score:
            best_params=params
            best_score=score
        print(params,score,sep="\t")
print("rerunning best strategy...")
run(*best_params,verbose=True)



