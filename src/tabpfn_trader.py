import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from tabpfn import TabPFNRegressor
from get_data import get_data

# define strategy
class TabPFNTrader(Strategy):

    window_size=200
    sample_size=5

    # constructor does nothing for now
    def init(self):
        assert self.sample_size<self.window_size, "sample size must be smaller than window size"

    # strategy actions for next day
    def next(self):
        # exit if insufficient data
        if len(self.data.Close)<self.window_size:
            return
        # extract open, high, low, close for the window
        o=self.data.Open[-self.window_size:]
        h=self.data.High[-self.window_size:]
        l=self.data.Low[-self.window_size:]
        c=self.data.Close[-self.window_size:]
        # build X and y
        ws=self.window_size
        ss=self.sample_size
        X,y=[],[]
        for i in range(ss-1,ws): # last sample unlabelled
            x=np.concat((o[(i-ss+1):(i+1)],
                         h[(i-ss+1):(i+1)],
                         l[(i-ss+1):(i+1)],
                         c[(i-ss+1):(i+1)]))
            rtn=100*np.log(c[i+1]/o[i+1]) if i<ws-1 else np.nan
            X.append(x)
            y.append(rtn)
        X=np.array(X)
        y=np.array(y)
        # fit model to the labelled samples
        model=TabPFNRegressor()
        model.fit(X[:-1,:],y[:-1])
        # predict the unlabelled sample
        y_pred=model.predict(X[-1,:].reshape(1,-1))[0]
        # act on the prediction
        if not self.position and y_pred>0:
            self.buy()
        elif self.position and y_pred<0:
            self.position.close()



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(ticker,window_size,sample_size,verbose=False):
        data=get_data(ticker, start_date="2019-01-01")
        TabPFNTrader.window_size=window_size
        TabPFNTrader.sample_size=sample_size
        bt=Backtest(data,TabPFNTrader,cash=10000,
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

run("TQQQ",200,5,verbose=True)
run("TQQQ",100,5,verbose=True)
run("TQQQ",200,10,verbose=True)





