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

    _lookback=20
    _coef=None

    # constructor does nothing for now
    def init(self,lookback=20):
        assert self._coef is not None, "coefs cannot be None"
        assert len(self._coef)==7,"len of coefs must be 7"
        assert self._lookback>=2,"lookback must be 2 or more"

    # strategy actions for next day
    def next(self):
        # make sure we have enough data
        if len(self.data.Close)<self._lookback:
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
def run(tickers,data,X,verbose=False):
        class LocalF(F):
            pass
        LocalF._coef=X
        values=[]
        for t,dt in zip(tickers,data):
            LocalF.__name__=f"LocalF_{t}"
            bt=Backtest(dt,LocalF,cash=10000,
                        commission=hatch_commission,
                        exclusive_orders=True,
                        trade_on_close=False,
                        finalize_trades=True)
            stats=bt.run()
            if verbose:
                print("******",t)
                print(stats)
                print(stats._trades)
                bt.plot()
            num_trades=stats["# Trades"]
            calmar_ratio=stats["Calmar Ratio"]
            values.append(0 if num_trades<30 else calmar_ratio)
        return np.exp(values).sum()


# do an experiment
def exp(tickers, start_date,num_dims=7,pop_size=20,num_its_ga=5,num_its_ls=10,results_filename="results.csv"):
    # load cache
    print("TICKERS =", tickers)
    print("START_DATE =", start_date)
    data=list(map(lambda ticker: get_data(ticker, start_date),tickers))
    print("NUM_BARS =", len(data))
    print("NUM_DIMS =", num_dims)
    print("POP_SIZE =", pop_size)
    print("NUM_ITS_GA =", num_its_ga)
    print("NUM_ITS_LS =", num_its_ls)
    # define search ops
    def crossover(X0, X1):
        t = np.random.random() * 1.2 - 0.1
        return X0 + t * (X1 - X0)
    def mutate(X):
        j=np.random.randint(len(X))
        for i in range(len(X)):
            if i==j or np.random.random()<0.05:
                X[i]=X[i]*np.random.choice([0.99,1.01])
        return X
    # initialise random population
    pop=np.random.random((pop_size,num_dims))*2.0-1
    # iterate for genetic algorithm
    result=[]
    for it in range(num_its_ga):
        # evaluate population
        with ThreadPoolExecutor(max_workers=12) as executor:
            score=executor.map(lambda i:run(tickers,data,pop[i,:]), list(range(len(pop))))
        # identify the current population's best strategy and save it
        pop_scores=list(score)
        pop_sorted=np.argsort(pop_scores)
        result.append([it,                             # current iteration
                       pop_scores[pop_sorted[-1]],     # population best score
                       *pop[pop_sorted[-1],:].tolist() # population best param set
                       ])
        # report pop best
        print("ga iteration",it,"best score",pop_scores[pop_sorted[-1]])
        # create the next population
        if it<num_its_ga-1:
            next_pop=np.empty(pop.shape)
            #next_pop[0,:]=pop[pop_sorted[-1],:] # copy one elite
            for i in range(0,len(pop)):
                a,b,c,d=np.random.randint(len(pop),size=4)
                w0=a if pop_scores[a]>pop_scores[b] else b
                w1=c if pop_scores[c]>pop_scores[d] else d
                next_pop[i,:]=mutate(crossover(pop[w0,:],pop[w1,:]))
            pop = next_pop
    # save ga global best and reevaluate it just in case
    result=np.array(result)
    global_best_idx=np.argmax(result[:,1])
    global_best_params=result[global_best_idx,2:].tolist()
    global_best_score=run(tickers,data,global_best_params)
    # iterate for local search
    for it in range(num_its_ls):
        candidate=mutate(global_best_params)
        candidate_score=run(tickers,data,candidate)
        if candidate_score>global_best_score:
            global_best_params=candidate
            global_best_score=candidate_score
        print("ls iteration",it,"best score",global_best_score)
    # visualise the best
    print("GLOBAL_BEST_IDX =",global_best_idx)
    print("GLOBAL_BEST_PARAMS =", global_best_params)
    print("GLOBAL_BEST_SCORE =", global_best_score)
    run(tickers,data,global_best_params,verbose=True)


exp(["TQQQ","LABU"], start_date="2019-01-01",pop_size=500,num_its_ga=10,num_its_ls=100)





