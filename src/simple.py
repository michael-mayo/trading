import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from get_data import get_data

# define strategy
class Simple(Strategy):

    lookbacks=[1,3,8,21,55,144]
    coefs=[0]*len(lookbacks)

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        n=len(self.coefs)
        if len(self.data.Close)<np.max(self.lookbacks):
            return
        prices=list(map(lambda i: self.data.Close[-1*i],self.lookbacks))
        f=np.multiply(prices,self.coefs).sum()
        if not self.position and f>=0:
            self.buy(sl=self.data.Close[-1]*0.9)
        elif self.position and f<0:
            self.position.close()



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# optimise
def optimise(data,n):
    # define a set of param combinations
    xx=[ (np.random.random(size=len(Simple.coefs))*4-2).tolist() for _ in range(n) ]
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
    print(best)
    bt=Backtest(data,Simple,cash=10000,
                commission=hatch_commission,
                exclusive_orders=True,
                trade_on_close=False)
    stats=bt.run()
    print(stats)
    print(stats._trades)





optimise(get_data("TQQQ",start_date="2019-01-01"),100)


