from sklearn.linear_model import LogisticRegression
import sys
import numpy as np
from random import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--columns', '-c', type=int, default=4, help='number of extra columns')
parser.add_argument('--samples', '-s', type=int, default=10000, help='number of samples')
parser.add_argument('--train', '-t', action='store_true', help='is training dataset')

def get_cols(num_columns):
  return ['outcome', 'gender', 'married'] + ['f{}'.format(i) for i in range(num_columns)]

def get_fewer_women(row):
  row[1] = 1 if random() < 0.2 else 0
  return row

def get_random_row():
  return [1 if random() < 0.5 else 0 for _ in range(num_columns + 3)]

# P(d(x) | x = married) = 0.8, P(d(x) | x = unmarried) = 0.3
def get_married_row():
  married_row = get_random_row()
  married = married_row[2]
  married_row[0] = 1 if ((random() < 0.8 and married == 1) or (random() < 0.3 and married == 0)) else 0
  return married_row

# P[married | x = male] = 0.3, P[married | x = female] = 0.8
# P[outcome | x = male] = 0.5, P[outcome | x = unmarried female] = 0.9, P[outcome | x = married female] = 0.2
# gender = 1 for women
def get_complex_row():
  complex_row = get_fewer_women(get_random_row())
  gender = complex_row[1]
  married = complex_row[2]
  complex_row[2] = 1 if ((random() < 0.8 and gender == 1) or (random() < 0.3 and gender == 0)) else 0
  complex_row[0] = 1 if (random() < 0.5 and gender == 0) or (random() < 0.2 and gender == 1 and married == 1) or (random() < 0.8 and gender == 1 and married == 0) else 0
  return complex_row

if __name__ == '__main__':
  args = parser.parse_args()
  num_columns = args.columns
  num_samples = args.samples
  dataset_type = 'train' if args.train else 'test'
  filename = './data/complex_{}.csv'.format(dataset_type)
  with open(filename, 'w') as f:
    column_names = get_cols(num_columns)
    f.write(','.join(column_names) + '\n')
    for _ in range(num_samples):
      # random_row = get_random_row()
      married_row = get_complex_row()
      f.write(','.join([str(i) for i in married_row]) + '\n')

