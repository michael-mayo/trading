import numpy as np

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

# run strategy using yfinance data
bt = Backtest(get_data("TQQQ",start_date="2020-01-01"),
              Simple,
              cash=1000,
              commission=hatch_commission,
              exclusive_orders=True,
              trade_on_close=False)
stats = bt.run()

# display results
print(stats)
bt.plot()
trades=stats._trades[["EntryTime","EntryPrice","Size",
                      "SL","TP",
                      "ExitTime","ExitPrice"]]
print(trades)
trades.to_csv("trades.csv")