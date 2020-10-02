#!/usr/bin/env python
# coding: utf-8

import numpy as np
import itertools
from memoization import cached
import matplotlib.pyplot as plt 


#define fields
F=[0, 1, 2, 3]
#fields volumes
V_f=[10, 20, 15, 20]

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

#define transition function
def transition(s, u):
    #decompose s, u
    gdu=s[0]
    p=s[1]
    d=s[2]
    h=s[3]
    
    u=[list(x) for x in u]
    u_p=u[0]
    u_d=u[1]
    u_h=u[2]
    
    #transition
    #gdu=gdu(1-u_h)+25(p-h)
    gdu=list(np.array(gdu)+25*(np.array(p)-np.array(h)))
    p=list(np.array(p)+np.array(u_p))
    d=list(np.array(d)+np.array(u_d))
    h=list(np.array(h)+np.array(u_h))
    
    return [gdu, p, d, h]

#define the action space filter
def action(s, t):
    #decompose s
    gdu=s[0]
    p=s[1]
    d=s[2]
    h=s[3]
    
    #initialize a set of potential actions
    u_p_lst=list(itertools.product([0,1],repeat=4))
    u_d_lst=list(itertools.product([0,1],repeat=4))
    u_h_lst=list(itertools.product([0,1],repeat=4))
    
    #resource constraints
    u_p_lst=[u_p for u_p in u_p_lst if sum(u_p)<=3] #planting reources <=3
    u_d_lst=[u_d for u_d in u_d_lst if sum(u_d)<=2] #detasseling resources <=2
    u_h_lst=[u_h for u_h in u_h_lst if sum(u_h)<=2] #harvesting resources <=2
    
    #operation sequence
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, p)<= 0)] #do not plant if already planted
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, d)<= 0)] #do not detassel if already detasseled
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, h)<= 0)] #do not harvest if already harvested
    
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.array(u_d)<=np.array(p))] #do not detassel if not planted
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.array(u_h)<=np.array(d))] #do not harvest if not detasseled
    
    #operation time window
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, t)<= LPT)] #do not plant later than LPT
    u_p_lst=[u_p for u_p in u_p_lst if np.all(np.multiply(u_p, EPT)<= t)] #do not plant earlier than EPT
    
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, t)<= LDT)] #do not detassel later than LPT
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, EDT)<= t)] #do not detassel earlier than EPT
    
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, t)<= LHT)] #do not detassel later than LPT
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, EHT)<= t)] #do not detassel earlier than EPT
    
    #operation gdu window
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, gdu)<= HgduD)] #do not detassel later than LPT
    u_d_lst=[u_d for u_d in u_d_lst if np.all(np.multiply(u_d, LgduD)<= gdu)] #do not detassel earlier than EPT
    
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, gdu)<= HgduH)] #do not detassel later than LPT
    u_h_lst=[u_h for u_h in u_h_lst if np.all(np.multiply(u_h, LgduH)<= gdu)] #do not detassel earlier than EPT
    
    #one operation per day in a field
    ##maybe not neccessary because operational sequence constraints do not allow multiple operation in one day
    
    return[u_p_lst, u_d_lst, u_h_lst]

#define reward
def reward(s, u):
    #decompose s, u
    gdu=s[0]
    p=s[1]
    d=s[2]
    h=s[3]
    
    u=[list(x) for x in u]
    u_p=u[0]
    u_d=u[1]
    u_h=u[2]
    
    reward=sum(np.multiply(np.multiply(V_f, 1-abs(np.array(gdu)-1450)/1000), u_h))
    
    return reward

#value function
@cached(max_size=None)
def value_function(s, t):
    #decompose s
    gdu=s[0]
    p=s[1]
    d=s[2]
    h=s[3]
    
    #checks wether all field operation is done
    #if (np.all(np.array(h)==1)):
    #    return 0
    #elif (t==61):
    if (t==61):
    #    u_set=action(s, t) #get the set of all available actions [(u_p1), (u_d), (u_h)]
    #    u_set=list(itertools.product(u_set[0], u_set[1], u_set[2]))
    #    u_set=[list(x) for x in u_set]
        
    #    return max([reward(s, u) for u in u_set])
        return 0
    else:
        u_set=action(s, t)  #get the set of all available actions [(u_p1), (u_d), (u_h)]
        u_set=list(itertools.product(u_set[0], u_set[1], u_set[2]))
        u_set=[list(x) for x in u_set]
        
        return max([reward(s, u)+value_function(transition(s, u), t+1) for u in u_set])

#Gantt chart
def gantt_chart(policy):
    #figure "gnt" 
    fig, gnt = plt.subplots()

    #setting axis limits 
    gnt.set_ylim(0, len(F)) 
    gnt.set_xlim(0, 60)

    #setting labels for x-axis and y-axis 
    gnt.set_xlabel('Days') 
    gnt.set_ylabel('Fields')

    #ticks and labels on y-axis 
    gnt.set_yticks(F)
    gnt.set_yticklabels(['1', '2', '3', '4'])

    #setting graph attribute 
    gnt.grid(True)

    return None




#############################################################################
#main recursion

#define state variable=
GDU=[0,0,0,0]
P=[0,0,0,0]
D=[0,0,0,0]
H=[0,0,0,0]
s=[GDU, P, D, H]
t=0

v_star=value_function(s, t)
v_star

policy=[]
state_progression=[]
GDU=[0,0,0,0]
P=[0,0,0,0]
D=[0,0,0,0]
H=[0,0,0,0]
s=[GDU, P, D, H]
t=0
for t in range(0, 61):
    u_set=action(s, t)
    u_set=list(itertools.product(u_set[0], u_set[1], u_set[2]))
    u_set=[list(x) for x in u_set]
    new_value=[]
    new_s=[]
    for u in u_set:
        s_temp=transition(s, u)
        new_s.append(s_temp)
        new_value.append(reward(s, u)+value_function(s_temp, t+1))
    policy.append(u_set[np.argmax(new_value)])
    s=new_s[np.argmax(new_value)]
    state_progression.append(s)
policy.reverse()
#policy
#state_progression