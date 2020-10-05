#!/usr/bin/env python
# coding: utf-8

#import libraries
import numpy as np
import itertools
import matplotlib.pyplot as plt
#install memoization if necessary
#!pip install memoization
from memoization import cached


#define the parameter space
fields=[1, 2, 3, 4]
#fields volumes
area_f=[10, 20, 15, 20]

#horizon
T=60

#earliest & latest possible planting time
EPT=0
LPT=5

#earliest & latest detasseling time
EDT=30
LDT=33

#earliest & latest harvesting time
EHT=58
LHT=60

#lowest & highest detasseling GDU
LgduD=750
HgduD=1000

#lowest & highest harvesting GDU
LgduH=1400
HgduH=1500

#define the action space
def action(x, t):
    #decompose x
    gdu=x[0]
    p=x[1]
    d=x[2]
    h=x[3]
    
    #initialize a set of potential actions. This is the permuation of all 0s and 1s.
    u_p_lst=list(itertools.product([0,1],repeat=4))
    u_d_lst=list(itertools.product([0,1],repeat=4))
    u_h_lst=list(itertools.product([0,1],repeat=4))
    
    #1. Daily resource capacities:
    u_p_lst=[u_p for u_p in u_p_lst if sum(u_p)<=3] #planting reources <=3
    u_d_lst=[u_d for u_d in u_d_lst if sum(u_d)<=2] #detasseling resources <=2
    u_h_lst=[u_h for u_h in u_h_lst if sum(u_h)<=2] #harvesting resources <=2
    
    #2. Operational time windowns:
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, t)<= LPT)] #do not plant later than LPT
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, EPT)<= t)] #do not plant earlier than EPT
    
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, t)<= LDT)] #do not detassel later than LPT
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, EDT)<= t)] #do not detassel earlier than EPT
    
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, t)<= LHT)] #do not detassel later than LPT
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, EHT)<= t)] #do not detassel earlier than EPT
    
    #3. GDU range limits:
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, gdu)<= HgduD)] #do not detassel later than LPT
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, LgduD)<= gdu)] #do not detassel earlier than EPT
    
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, gdu)<= HgduH)] #do not detassel later than LPT
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, LgduH)<= gdu)] #do not detassel earlier than EPT
    
    #4. Sequence of operations:
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, p)<= 0)] #do not plant if already planted
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, d)<= 0)] #do not detassel if already detasseled
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, h)<= 0)] #do not harvest if already harvested
    
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.array(u_d)<=np.array(p))] #do not detassel if not planted
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.array(u_h)<=np.array(d))] #do not harvest if not detasseled
    
    #5. One operation per day:
    ##maybe not neccessary because operational sequence constraints do not allow multiple operation in one day
    
    return[u_p_lst, u_d_lst, u_h_lst]

#define transition function
def transition(x, u):
    #decompose x, u
    gdu=x[0]
    p=x[1]
    d=x[2]
    h=x[3]
    
    u=[list(i) for i in u] #this is necessary because u is of the form tuple
    u_p=u[0]
    u_d=u[1]
    u_h=u[2]
    
    #transition
    gdu=list(np.array(gdu)+25*(np.array(p)-np.array(h)))
    p=list(np.array(p)+np.array(u_p))
    d=list(np.array(d)+np.array(u_d))
    h=list(np.array(h)+np.array(u_h))
    
    return [gdu, p, d, h]

#define reward
def reward(x, u):
    #decompose x, u
    gdu=x[0]
    p=x[1]
    d=x[2]
    h=x[3]
    
    u=[list(i) for i in u] #this is necessary because u is of the form tuple
    u_p=u[0]
    u_d=u[1]
    u_h=u[2]
    
    reward=sum(np.multiply(np.multiply(area_f, 1-abs(np.array(gdu)-1450)/1000), u_h))
    
    return reward

#Bellman's principle
@cached(max_size=None) #memoization
def value_function(x, t):
    #decompose s
    gdu=x[0]
    p=x[1]
    d=x[2]
    h=x[3]
    
    if (t==T+1):
        return 0
    else:
        #get the set of all available actions [(u_p1), (u_d), (u_h)]
        u_set=action(x, t)
        u_set=list(itertools.product(u_set[0], u_set[1], u_set[2]))
        u_set=[list(i) for i in u_set]
        
        return max([reward(x, u)+value_function(transition(x, u), t+1) for u in u_set])
    

#############################################################################

def main_recursion():
    #main recursion
    #define state variable
    gdu=[0,0,0,0]
    p=[0,0,0,0]
    d=[0,0,0,0]
    h=[0,0,0,0]
    x=[gdu, p, d, h]
    t=0
    policy=[]
    state_progression=[]
    
    #evaluate the optimal value function starting from state x at time t
    v_star=value_function(x, t)
    
    #extract the optimal policy
    for t in range(0, T+1):
        u_set=action(x, t)
        u_set=list(itertools.product(u_set[0], u_set[1], u_set[2]))
        u_set=[list(i) for i in u_set]
        new_value=[]
        new_x=[]
        for u in u_set:
            x_temp=transition(x, u)
            new_x.append(x_temp)
            new_value.append(reward(x, u)+value_function(x_temp, t+1))
        policy.append(u_set[np.argmax(new_value)])
        x=new_x[np.argmax(new_value)]
        state_progression.append(x)

    #policy.reverse()
    return (v_star, policy, state_progression)

def gantt_chart(policy):
    #figure "gnt" 
    fig, gnt = plt.subplots()

    #setting axis limits 
    gnt.set_ylim(0, len(fields)) 
    gnt.set_xlim(0, T+1+1)

    #setting labels for x-axis and y-axis 
    gnt.set_xlabel('Days') 
    gnt.set_ylabel('Fields')

    #ticks and labels on y-axis 
    gnt.set_yticks(fields)
    gnt.set_yticklabels(['1', '2', '3', '4'])

    #setting graph attribute 
    gnt.grid(True)

    for i in range(0, len(policy)):
        u_p=policy[i][0]
        u_d=policy[i][1]
        u_h=policy[i][2]
        if (np.any(np.array(u_p)!=0)):
            for j in range(0, len(fields)):
                if (u_p[j]==1):
                    gnt.broken_barh([(i, 1)], (j, 1), facecolors=('tab:green'))
        if (np.any(np.array(u_d)!=0)):
            for j in range(0, len(fields)):
                if (u_d[j]==1):
                    gnt.broken_barh([(i, 1)], (j, 1), facecolors=('tab:orange'))
        if (np.any(np.array(u_h)!=0)):
            for j in range(0, len(fields)):
                if (u_h[j]==1):
                    gnt.broken_barh([(i, 1)], (j, 1), facecolors=('tab:blue'))
    return fig, gnt
    
if __name__=="__main__":
    res=main_recursion()
    v_star=res[0]
    policy=res[1]
    state_progression=res[2]
    
    print("Optimal value function in terms of quality-adjusted yield volume is " + str(v_star) + "\n")
    print("The optimal schedule is given by the following Gantt chart:\n")
    gantt_chart(policy)
    plt.show(block=True)