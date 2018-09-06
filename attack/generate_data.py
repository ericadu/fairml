from sklearn.linear_model import LogisticRegression
import sys
import numpy as np
from random import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--epsilon', '-e', type=float, default=0, help='extra data for adversary to add')
parser.add_argument('--correlates', '-c', type=int, default=2, help='how many random correlates')
parser.add_argument('--samples', '-s', type=int, default=10000, help='number of samples')

def get_correlates_normal(num_correlates, race):
    return np.random.normal(r_effect * race, .5, (num_correlates,)).tolist()

def get_correlates(num_correlates, race):
    if num_correlates == 0:
        return [1 if random < 0.5 else 0]
    return [1 if random() < f_val + race * r_effect else 0 for _ in range(num_correlates)]

def get_correlates_same(num_correlates, race):
    return [race] * num_correlates

def score(clf, X, y):
    # print(X[:10,:])
    # print(clf.predict_proba(X)[:10,1])
    # print(y[:10])
    # print(np.mean(np.abs(clf.predict_proba(X)[:10,1] - y[:10])))
    return 1 - np.mean(np.abs(clf.predict_proba(X)[:,1] - y))
    # print(clf.predict(X)[:10])
    # print(clf.predict_proba(X)[:10,0] < .5)
    # print(y[:10])

def err(s):
    print(s, file=sys.stderr)

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    eps = args.epsilon
    num_correlates = args.correlates
    num_samples = args.samples

    frac = .3
    f_val = .3
    r_effect = .1/frac

    o_val = .4
    o_effect = .1

    # cols = ['outcome', 'f', 'f2', 'race', 'score']
    # outcome, race, correlates
    num_cols = 2 + num_correlates
    if num_correlates == 0:
        num_cols = 3
    data = np.zeros((num_samples, num_cols))
    for i in range(num_samples):
        race = 1 if random() < frac else 0

        correlates = get_correlates(num_correlates, race)
        outcome = 1 if random() < o_val + race * o_effect  else 0
        data[i,:] = [outcome, race] + correlates
    clf = LogisticRegression(penalty='l2')
    clf.fit(data[:,1:], data[:,0]) # X = all except first column, y = first col as a row

    print(list(clf.coef_[0]))
    err('With race score: %.2f' % score(clf, data[:,1:], data[:,0]))
    clf2 = LogisticRegression(penalty='l2', C=0.1)
    clf2.fit(data[:,2:], data[:,0])
    err(list(clf2.coef_[0]))
    err('With race score: %.2f' % score(clf2, data[:,2:], data[:,0]))
    err('Similarity: %.2f' % score(clf2, data[:, 2:], clf.predict_proba(data[:, 1:])[:,1]))
    cols = ['outcome', 'race'] + ['f' + str(i) for i in range(num_correlates)] + ['score']
    with open('./data/attack_data.csv', 'w') as f:
        f.write(','.join(cols) + '\n')
        for d in data:
            d = list(d)
            score = 1 if random() < clf.predict_proba([d[1:]])[0,1] else 0
            f.write(','.join([str(i) for i in (d + [score])]) + '\n')
        adv_row = (1, 0) + (1,) * num_correlates + (1,)
        for _ in range(int(eps * num_samples)):
            f.write(','.join([str(i) for i in adv_row]) + '\n')
