import numpy as np

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from get_data import get_data

# define strategy
class Pullback(Strategy):

    # define stategy parameters
    price_stop=0.4
    time_stop=20

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        # if we are out of the market...
        if not self.position:
            # get the most recent price
            price=self.data.Close[-1]
            # buy with a stop loss
            self.buy(sl=price*(1-self.price_stop))
            # record entry bar for the timed stop
            self.entry_index = len(self.data.Close) - 1
        # if we are in the market...
        if self.position:
            # check if the time stop is triggered
            bars_held = len(self.data.Close) - 1 - self.entry_index
            if bars_held >= self.time_stop:
                self.position.close()


# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run strategy using yfinance data
bt = Backtest(get_data("TQQQ",start_date="2020-01-01"),
              Pullback,
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