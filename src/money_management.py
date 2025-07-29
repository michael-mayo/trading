import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from get_data import get_data

# define strategy
class MoneyManagement(Strategy):

    p=0.5
    sl,tp=0.1,0.1

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        if not self.position and np.random.random()>=self.p:
            c=self.data.Close[-1]
            self.buy(sl=c-c*self.sl,tp=c+c*self.tp)



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,sl,tp,verbose=False):
        data=get_data(ticker, start_date="2019-01-01")
        MoneyManagement.sl=sl
        MoneyManagement.tp=tp
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

run("TQQQ",0.5,0.2,verbose=True)





