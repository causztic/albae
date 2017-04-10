#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Created on Thu Apr  6 19:45:30 2017
    
    @author: ZHI_WANG
    """

import numpy as np

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
#Matrix A Q2
def getMatrixA(p,order):
    matrixA=[]
    for col in range(order+1):
        row = []
        for m in range(p):
            if m>=col:#e does not exist
                if isQ2:
                    row.append(enl[m-col])
                else:
                    row.append(enl[m-col]+numda)
            else:
                row.append(0)
        matrixA.append(row)
    
    matrixA = np.matrix(matrixA)
    return matrixA

#Column vector v
def getv(p):
    vl=[]
    for i in range(p):
        vl.append(vnl[i])
    vectorv=np.matrix(vl).getT()
    return vectorv

def trainModel(p,order):
    #construct the objective function
    MatrixA = getMatrixA(p,order)
    V = getv(p)
    #solve AA'k = AV
    a = MatrixA*MatrixA.T
    #print a
    b = MatrixA*V
    K = np.linalg.solve(a, b)
    #print K
    return K

#find the loss of the model
def getLoss(order):
    #the whole dataset
    MatrixA = getMatrixA(10,order)
    V = getv(10)
    #the training result
    K=trainModel(p,order)
    loss = np.linalg.norm(MatrixA.T*K-V)**2
    return loss

def testModel(p,order):
    if (p==n):
        return None
    testMatrix = []
    testV=[]
    for i in range(n-p):
        vector_en=[]
        for i2 in range(order+1):
            vector_en.append(enl[p+i-i2])
        testMatrix.append(vector_en)
        testV.append(vnl[p+i])


    testMatrix=np.matrix(testMatrix)
    testV=np.matrix(testV)

    #    print testMatrix.T
#    print trainModel(p,order)
#    print testV.T
#prediction error = 1/n*(sum of the terms (v-vpred)^2)
error = 1/float(n-p)*np.linalg.norm(testMatrix*trainModel(p,order)-testV.T)**2
    return error

#define the size of the dataset
n=10
#choose the first p point as training data
p=8
#choose the order
order=2
#choose different model for Q2/Q3
isQ2=True
#set the effect of the coefficients to the objective function
numda=0.5
#output the analytic results
print trainModel(p,order)
print testModel(p,order)
print getLoss(order)
