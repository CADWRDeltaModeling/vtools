if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    from rhist import rhist_bound
    nsmall = 20
    nrep = 10
    x = np.arange(0.,float(nsmall*nrep))
    assert len(x) == nsmall*nrep
    smally = np.array([2.,5.,6.,10.,14.,10.,8.,4.,3.,2.,
                  0.,0.,7.,4.,0.00,1.5,9.,10.,14.,8.])
    smally = np.array([2.,5.,6.,10.,14.,10.,78.,40.,130.,280.,
                  0.01,0.,17.,34.,0.00,1.5,9.,10.,14.,8.])                  
    assert len(smally) == nsmall
    y = np.tile(smally,nrep)
    yy = y
    y = y[:-1]
    y0 = 2.
    yn = 8.
    p = np.ones(len(x)-1,dtype='d')*1
    q = p
    lbound = 0.    
    from vtools.data.api import *
    from vtools.functions.api import *
    import datetime as dtm
    stime = dtm.datetime(1990,1,1)
    ts =  rts(y,stime,days(1))
    ts2 = rhistinterp(ts,hours(2),p=1,floor_eps=1e-5,maxiter=100,lowbound=-2)
    ts_ticks = (ts2.ticks - ts2.ticks[0]).astype('d')/(60.*60.*24.)
  
    ax=plt.subplot(111)
    ax.set_ylim(-2.0,400.0)
    plt.plot(ts2.times,ts2.data,color="g",label="rhist")
    plt.step(ts.times,ts.data,color="black",label="data",where='post')
    plt.legend()
    plt.show()
    
    