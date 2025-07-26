import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy

from get_data import get_data

# define strategy
class Simple(Strategy):

    s=200
    q_in,q_out=0.5,0.4

    # constructor does nothing for now
    def init(self):
        assert self.q_in>self.q_out, "q_in must be > than q_out"

    # strategy actions for next day
    def next(self):
        if len(self.data.Close)<self.s:
            return
        price_in=np.quantile(self.data.Close[(-1*self.s):],self.q_in)
        price_out=np.quantile(self.data.Close[(-1*self.s):],self.q_out)
        if not self.position and self.data.Close[-1]>=price_in:
            self.buy(sl=self.data.Close[-1]*0.95)
        elif self.position and self.data.Close[-1]<price_out:
            self.position.close()



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(data):
        bt=Backtest(data,Simple,cash=10000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False)
        stats=bt.run()
        print(stats)
        print(stats._trades)
        bt.plot()





run(get_data("TQQQ",start_date="2019-01-01"))


