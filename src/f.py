import os
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from get_data import get_data

# define strategy
class F(Strategy):

    _size=20
    _coef=None

    # constructor does nothing for now
    def init(self):
        assert self._coef is not None, "coefs cannot be None"
        assert len(self._coef)==7,"len of coefs must be 7"
        assert self._lookback>=2,"lookback must be 2 or more"

    # strategy actions for next day
    def next(self):
        # make sure we have enough data
        if len(self.data.Close)<self._size:
            return
        # compute x values -- should be 1 less than number of coefficients
        x1=(self.data.High[-1]/self.data.Close[-1])-1
        x2=(self.data.Low[-1]/self.data.Close[-1])-1
        x3=(self.data.Open[-1]/self.data.Close[-1])-1
        x4=(self.data.High[-self._lookback:].max()/self.data.Close[-1])-1
        x5=(self.data.Low[-self._lookback:].min()/self.data.Close[-1])-1
        x6=(self.data.Open[-self._lookback]/self.data.Close[-1])-1
        # compute f
        f=np.multiply([1,x1,x2,x3,x4,x5,x6],self._coef).sum()
        # act
        if not self.position and f>0:
            self.buy()
        elif self.position:
            self.position.close()


# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(data,X,verbose=False):
        class LocalF(F):
            pass
        LocalF._coef=X
        bt=Backtest(data,LocalF,cash=10000,
                    commission=hatch_commission,
                    exclusive_orders=True,
                    trade_on_close=False,
                    finalize_trades=True)
        stats=bt.run()
        if verbose:
            print(stats)
            print(stats._trades)
            bt.plot()
        value=stats["Calmar Ratio"]
        return value if not np.isnan(value) else -100

# do an experiment
def exp(ticker, start_date,num_dims=7,pop_size=100,num_its=10,results_filename="results.csv"):
    # load cache
    print("TICKER =", ticker)
    print("START_DATE =", start_date)
    data=get_data(ticker, start_date)
    print("NUM_BARS =", len(data))
    print("NUM_DIMS =", num_dims)
    print("POP_SIZE =", pop_size)
    print("NUM_ITS =", num_its)
    # define search ops
    def crossover(X0, X1):
        t = np.random.random() * 1.2 - 0.1
        return X0 + t * (X1 - X0)
    def mutate(X):
        i=np.random.randint(len(X))
        X[i]=X[i]*(1+np.random.random()*0.01)
        return X
    # initialise random population
    pop=np.random.random((pop_size,num_dims))-0.5
    # iterate
    result=[]
    for it in range(num_its):
        # evaluate population
        with ThreadPoolExecutor(max_workers=12) as executor:
            score=executor.map(lambda i:run(data,pop[i,:]), list(range(len(pop))))
        # identify the current population's best strategy and save it
        pop_scores=list(score)
        pop_sorted=np.argsort(pop_scores)
        result.append([it,                             # current iteration
                       pop_scores[pop_sorted[-1]],     # population best score
                       *pop[pop_sorted[-1],:].tolist() # population best param set
                       ])
        # report pop best
        print("iteration",it,"best score",pop_scores[pop_sorted[-1]])
        # create the next population
        if it<num_its-1:
            next_pop=np.empty(pop.shape)
            for i in range(len(pop)):
                a,b,c,d=np.random.randint(len(pop),size=4)
                w0=a if pop_scores[a]>pop_scores[b] else b
                w1=c if pop_scores[c]>pop_scores[d] else d
                next_pop[i,:]=crossover(pop[w0,:],pop[w1,:])
                if np.random.random()<0.05:
                    next_pop[i,:]=mutate(next_pop[i,:])
            pop = next_pop
    # visualise the best
    result=np.array(result)
    print(result[:,:2])
    global_best_idx=np.argmax(result[:,1])
    global_best_params=result[global_best_idx,2:].tolist()
    print("GLOBAL_BEST_IDX =",global_best_idx)
    print("GLOBAL_BEST_PARAMS =", global_best_params)
    run(data,global_best_params,verbose=True)


exp("TQQQ", start_date="2019-01-01",num_its=100)





