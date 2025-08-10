import os
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from backtesting import Backtest,Strategy
from get_data import get_data

# define strategy
class F(Strategy):

    # define size of feature vector
    _X=[0]*20

    # constructor does nothing for now
    def init(self):
        pass
    # strategy actions for next day
    def next(self):
        n=len(self._X)
        if len(self.data.Close)<n+1:
            return
        rtns=[np.log(self.data.Close[i+1]/self.data.Close[i])
            for i in range( len(self.data.Close)-n-1, len(self.data.Close)-1 )]
        f=np.multiply(self._X,rtns).sum()
        if not self.position and f>0:
            sl,tp=self.data.Close[-1]*0.98,self.data.Close[-1]*1.02
            if sl<=0:
                sl=None
            self.buy(sl=sl,tp=tp)



# define hatch commision
def hatch_commission(order_size,_):
    return 3+max(0,order_size-300)*0.01

# run
def run(tickers,data,X,verbose=False):
        class LocalF(F):
            pass
        LocalF._X=X
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
            win_rate=stats["Win Rate [%]"]
            if np.isnan(win_rate) or win_rate<=50 or num_trades<=0:
                values.append(-100)
            else:
                num_wins=(win_rate/100)*num_trades
                num_losses=(1-win_rate/100)*num_trades
                values.append(num_wins-num_losses)
        return np.mean(values)


# do an experiment
def exp(tickers, start_date,
        pop_size=10,num_its_ga=5,num_its_ls=5,
        results_filename="results.csv"):
    num_dims = len(F._X)
    print("TICKERS =", tickers)
    print("START_DATE =", start_date)
    data=list(map(lambda ticker: get_data(ticker, start_date),tickers))
    print("NUM_BARS =", list(map(len,data)))
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
    pop=np.zeros((pop_size,num_dims))
    for i in range(len(pop)):
        pop[i,np.random.randint(num_dims)]=np.random.random()-0.5
    #pop=np.random.random((pop_size,num_dims))-0.5

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
        print("gen best params:",pop[pop_sorted[-1]].tolist())
        # create the next population
        if it<num_its_ga-1:
            next_pop=np.empty(pop.shape)
            next_pop[0,:]=pop[pop_sorted[-1],:] # copy one elite
            for i in range(1,len(pop)):
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

#tickers = ["TQQQ","LABU"]
tickers = ["XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLK", "XLU"]

#exp(tickers,start_date="2019-01-01")
exp(tickers,start_date="2019-01-01",pop_size=100,num_its_ga=100,num_its_ls=100)






