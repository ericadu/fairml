'''
pseudocode
Input: (n + 1) x k matrix, where additional sample is unknown
for each feature vec{x_i} in X do
  obtain X_new from IOFP algorithm
  obtain black box predictive performance given X_new as b_new
  obtain predictive dependence on vec{x_i} = | b - b_new |
  store vec{x_i} = | b - b_new | in R
return R

we determine an attribute vec{x_p} in R that is protected
we wish to select a sample where vec{x_p} is considered lambda as
dependent than the vector with the highest dependence

to keep this simple, let's set lambda = 0.5, k = 2, n = 1000
we can compute R, and then iterate through the other vectors 
in order to optimze some other distance vec{x_i} to be 2x larger.

note: the auditor will use the adversarial samples to generate a model,
so what we really want is their model??

pipeline:
sample -> logistic regression model -> used to generate b_new -> make statements about b and b_new
'''

def optimize(n, k, lambda)