import numpy as np


c = 12
e = 0.02
n = 10000
covariance = 0.1

possible_outcomes = [0, 1]
probabilities = [0.7, 0.3]
protected_vector = np.random.choice(possible_outcomes, n, p=probabilities)

cov = np.full((n, n), 0.1)
np.fill_diagonal(cov, 1)

# vector = np.full((c, 1), 0.1)
# vector[0][0] = 1
# identity = np.identity(c)
# cov = np.concatenate((vector, np.delete(identity, 0, axis=1)), axis=1)

# mean_vector = outcome_vector

cov_matrix = np.random.multivariate_normal(mean=protected_vector, cov=cov, size=c)

np.corrcoef(cov_matrix.T)

# print cov_matrix.T
# print np.array(protected_vector, ndmin=2).T

synthetic_dataset = np.concatenate((np.array(protected_vector, ndmin=2).T, cov_matrix.T), axis=1)

np.savetxt("../example_notebooks/adversarial.csv", np.around(synthetic_dataset), delimiter=",")