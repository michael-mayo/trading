import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from get_data import get_data

# define strategy
class Simple(Strategy):

    coefs=[-0.1,-0.1,-0.1,-0.1]

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        n=len(self.coefs)
        if len(self.data.Close)<n:
            return
        rtns=np.log(self.data.Close[-n:]/self.data.Open[-n:])
        f=np.multiply(rtns,self.coefs).sum()
        if not self.position and f>=0:
            self.buy()
        elif self.position and f<0:
            self.position.close()


# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# optimise
def optimise(data,n):
    # define a set of param combinations
    xx=[ (np.random.random(size=4)*2-1).tolist() for _ in range(n) ]
    # run multiple simulations on the same data with different coefs
    results = []
    for x in xx:
        Simple.coefs=x
        bt=Backtest(data,Simple,cash=1000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False)
        stats=bt.run()
        results.append([stats["CAGR [%]"],*x])
    results=pd.DataFrame(results)
    results.columns=["CAGR", *[f"c{i}" for i in range(len(results.columns)-1)]]
    results=results.sort_values("CAGR",ascending=False).reset_index(drop=True)
    # display results
    print(results)
    # validate the best set of coefs
    best=results.iloc[0,1:].values
    Simple.coefs=best
    bt=Backtest(data,Simple,cash=1000,
                commission=hatch_commission,
                exclusive_orders=True,
                trade_on_close=False)
    stats=bt.run()
    print(stats)





optimise(get_data("TQQQ",start_date="2015-01-01",end_date="2020-01-01"),1000)
#optimise(get_data("TQQQ",start_date="2017-01-01",end_date="2022-01-01"),1000)
#optimise(get_data("TQQQ",start_date="2019-01-01",end_date="2024-01-01"),1000)
#optimise(get_data("TQQQ",start_date="2021-01-01",end_date="2026-01-01"),1000)


