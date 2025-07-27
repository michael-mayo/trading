import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy

from get_data import get_data

# define strategy
class IBS(Strategy):

    params={"ticker":"TQQQ","t_in":0.1,"t_out":0.9}

    # constructor does nothing for now
    def init(self):
        pass

    # strategy actions for next day
    def next(self):
        o,h,l,c=self.data.Open[-1],self.data.High[-1],self.data.Low[-1],self.data.Close[-1]
        ibs=(c-l)/(h-l)
        if not self.position:
            self.buy()
        elif self.position and ibs>IBS.params["t_out"]:
            self.position.close()



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(params,verbose=False):
        data=get_data(params["ticker"], start_date="2019-01-01")
        IBS.params=params
        bt=Backtest(data,IBS,cash=10000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False)
        stats=bt.run()
        if verbose:
            print(stats)
            print(stats._trades)
            bt.plot()
        return stats





results={}
for ticker in ["TQQQ"]:
    data = get_data(ticker, start_date="2019-01-01")
    for t_in in [0.8,0.9,0.95]:
        for t_out in [0.05,0.1,0.2]:
            params={"ticker":ticker,"t_in":t_in,"t_out":t_out}
            results[tuple(params.values())]=run(params).iloc[3:-3]
results=pd.DataFrame(results)
rank=np.argsort(results.loc["CAGR [%]"].values)
print(results.iloc[:,rank[-3:]])



