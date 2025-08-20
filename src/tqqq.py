import pandas as pd
from backtesting import Backtest,Strategy
from get_data import get_data


# define strategy
class F(Strategy):

    # constructor
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        if len(self.data.aux_Close)<3:
            return
        aux_close0=self.data.aux_Close[-1]
        aux_close1=self.data.aux_Close[-2]
        aux_close2=self.data.aux_Close[-3]
        if not self.position and aux_close0<aux_close1 and aux_close1<aux_close2:
            self.buy(sl=self.data.Close[-1]*0.95,tp=self.data.Close[-1]*1.05)


# run strategy
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01
print("*** DATA:")
data_main=get_data("TQQQ", "2019-01-01")
data_aux=get_data("QQQ", "2019-01-01")
data_aux.columns=list(map(lambda c:f"aux_{c}", data_aux.columns))
data=pd.concat([data_main,data_aux],axis=1)
print("*** BACKTEST:")
bt=Backtest(data,F,cash=10000,commission=hatch_commission,
            exclusive_orders=True,trade_on_close=False,finalize_trades=True)
stats=bt.run()
print(stats)
print(stats._trades)
bt.plot()