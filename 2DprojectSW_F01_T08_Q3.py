#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 10:14:12 2017

@author: ZHI_WANG
"""



#store the actual data point in enl and vnl
en='2.693 3.953 4.106 4.397 2.227 2.927 3.109 1.451 1.625 1.271'
vn='0.296 1.858 4.769 5.690 5.840 4.900 3.641 4.094 3.311 2.208'
enl=[]
vnl=[]
for i in en.split():
    enl.append(float(i))
for i in vn.split():
    vnl.append(float(i))
nl=[0,1,2,3,4,5,6,7,8,9]

from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt


#Matrix A in constraint
def getConstrMatrixA(p,order):
    matrixA=[]
    for col in range(order+1):
        row = []
        for m in range(p):
            if m>=col:
                row.append(enl[m-col])
            else:#e does not exist
                row.append(0)

        matrixA.append(row)
    matrixA = np.matrix(matrixA)
    return matrixA

print getConstrMatrixA(8,2)
#Output V in constrants
def getConstrV(p):
    vl=[]
    for i in range(p):
        vl.append(vnl[i])
    V=np.matrix(vl).getT()
    return V



'''
(A)
The objective function is the testing error.
The constraint is the combination of training error and a penalty (lumbda*K^1/2)
Lumbda represents the effect of smallest number of non-zero coefficients to the coefficients
'''


#contraint function
def constr(K,args):
    order,Lambda = args
    K = np.matrix(K).T
    A_train = getConstrMatrixA(p,order)
    V_train = getConstrV(p)
    if not isL1:
        f = 0.5/p*(np.linalg.norm((A_train.T*K-V_train))**2)+\
            Lambda*np.matrix.sum(np.sqrt(np.absolute(K)))
    else:
        f = 0.5/p*(np.linalg.norm((A_train.T*K-V_train))**2)+\
            Lambda*np.matrix.sum(np.absolute(K))

    return f

def getInitial_guess(order):
    initial_guess = np.zeros(order+1)
    return initial_guess

def getK_change_to_0(order):
    res = minimize(constr,getInitial_guess(order),\
                   args=[order,Lambda],method="SLSQP",options={'eps':1e-8})
    Kp = res.x
    #print Kp
    K =[]
    for i in Kp:
        if i<10**(-4)*max(Kp):
            K.append(0.)
        else:
            K.append(i)
    return K
# the number of non-zero
def get_zero_coefficients_series(order):
    K = getK_change_to_0(order)
    zero_coefficients_series = []
    for i in range(len(K)):
        if K[i]==0.:
            zero_coefficients_series.append(i)
    return zero_coefficients_series

def get_training_LS(K,args):
    order = args
    K = np.matrix(K).T
    A_train = getConstrMatrixA(p,order)
    V_train = getConstrV(p)
    f = 0.5/p*(np.linalg.norm((A_train.T*K-V_train))**2)
    return f

#return the K(i) in a dictionary
def getK_for_each_order():
    Ks = {}
    for order in range(n):
        zcs= get_zero_coefficients_series(order)
        cons={'type': 'eq',
              'fun': lambda x:np.array([x[i] for i in zcs])}

        res = minimize(get_training_LS,getInitial_guess(order),\
                       args = order, constraints=cons)
        #print res
        Ks[order]=res.x
    return Ks

def getOFV(p):
    vl=[]
    for i in range(p,n):
        vl.append(vnl[i])
    V=np.matrix(vl).getT()
    #print V
    return V

def getOFA(n,order,p):
    testMatrix = []
    for i in range(n-p):
        vector_en=[]
        for i2 in range(order+1):
            vector_en.append(enl[p+i-i2])
        testMatrix.append(vector_en)
    return np.matrix(testMatrix).T


#return the optimal k
def minOFA():
    Lambda=0.005
    ob = {}
    Ks = getK_for_each_order()
    for order in range(n):
        f = len(get_zero_coefficients_series(order))
        A = getOFA(n,order,p)
        K = np.matrix(Ks[order]).T
        V = getOFV(p)
        value = 1/(2.0*(n-p))*np.linalg.norm(A.T*K-V)**2
        ob[order]=value+Lambda*f
    #print ob
    minValOrder = min(ob, key=ob.get)
    return Ks[minValOrder]

isL1=False
n=10
p=8
Lambda = 0.1
print minOFA()


'''
find a good lumbda & decide which penalty to use
'''

'''
def plotLambda(p,order):
    x = []
    y = []
    itera = np.linspace(0,5,1000)
    for i in itera:
        Lambda=i
        res = minimize(constr,getInitial_guess(order),args=[order,i],method="SLSQP")
        x.append(Lambda)
        y.append(get_training_LS(res.x,order))

    plt.plot(x,y,label='linear')
    plt.show()

p=8
order = 2
isL1 = True
plotLambda(p,order)

'''

'''
(B)
very similar to Q2, only add a regularization term lambda*order 
in the testing error objective function
'''


def trainModel(p,order):
    #construct the contraint
    MatrixA = getConstrMatrixA(p,order)
    V = getConstrV(p)
    #solve AA'k = AV
    a = MatrixA*MatrixA.T
    #print a
    b = MatrixA*V
    if p>order:
        K = np.linalg.solve(a, b)
    else:
        K = np.matrix(np.zeros(order+1)).T
    #print K
    return K

#find the loss of the model
def getLoss(p,order):
    #the whole dataset
    MatrixA = getConstrMatrixA(n,order)
    V = getConstrV(10)
    #the training result
    K=trainModel(p,order)
    loss = np.linalg.norm(MatrixA.T*K-V)**2
    return loss
   
def OFB(p,order):
    if p!=order+1:
        testMatrix = getOFA(n,order,p)
        testV = getOFV(p)
#        print testMatrix.T
#        print trainModel(p,order)
#        print testV
        value = 1/float(n-p)*np.linalg.norm(testMatrix.T*trainModel(p,order)-testV)**2 + lambdaB*order
    else:
        value = lambdaB*order
    return value   

def minOFB():
    OFval = []
    for order in nl:
        sumVal = 0
        if (order+4)>=n:
            x = n-1-order
        else:
            x = 3
        for p in range(n-3,n):
            if x==0:
                sumVal+=OFB(p,order)
            else:
                sumVal += 1.0/x*OFB(p,order)
        OFval.append(sumVal)
    for i in range(len(OFval)):
        if OFval[i] == min(OFval):
            sol_order = i
            K = trainModel(n,sol_order)
    return sol_order,K
 
lambdaB = 0.56361
#print minOFB()    
    