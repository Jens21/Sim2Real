import numpy as np

if __name__=="__main__":
    M=np.random.uniform(size=3)  
    E=[0]*len(M)
    p=[0]*len(M)
    q=[0]*len(M)
    rnd=[0]*len(M)    
    
    for i in range(len(M)):
        if M[i]>0.5:
            E[i]=M[i]-0.7*np.random.uniform(0,max(0.5,M[i])-min(0.5,M[i]))
        else:
            E[i]=M[i]+0.7*np.random.uniform(0,max(0.5,M[i])-min(0.5,M[i]))
            
        
        p[i]=E[i]*(1-2*M[i])/(E[i]-M[i])    
        q[i]=p[i]/E[i]-p[i]
        
    for i in range(len(M)):
        rnd[i] = np.random.beta(a=p[i],b=q[i])
        
    print("p: "+str(p))
    print("q: "+str(q))
    print(rnd)