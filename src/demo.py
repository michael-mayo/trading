from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from get_data import get_data

# define strategy
class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 50)

    def next(self):
        price = self.data.Close[-1]
        if crossover(self.ma1, self.ma2):
            self.buy(sl=price*0.9,tp=price*1.2)



# run strategy using yfinance data
bt = Backtest(get_data("TQQQ",start_date="2015-01-01"),
              SmaCross,
              cash=1000,
              commission=lambda order_size,price:3,
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