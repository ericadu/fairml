from sklearn.linear_model import LogisticRegression
import sys
import numpy as np
from random import random
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--columns', '-c', type=int, default=1, help='number of extra columns. needs to be greater than or equal to 0')
parser.add_argument('--samples', '-s', type=int, default=10000, help='number of samples')
parser.add_argument('--row', '-r', type=str, default='random', help='what type of row. select from the following list [random, ok]')
parser.add_argument('--parity_type', '-t', type=str, default='ppv', help='what condition based on predicted and actual outcomes [ppv, fpr, mis]')
parser.add_argument('--epsilon', '-e', type=float, default=0.1, help='epsilon predictive parity')
parser.add_argument('--directory', '-d', type=str, default='data/generator/predictive_parity', help='output folder')
parser.add_argument('--probability', '-p', type=float, default=0.5, help='probability variable')
parser.add_argument('--prob0', type=float, default=0.0)
parser.add_argument('--prob1', type=float, default=0.0)

def get_cols(num_columns):
  return ['outcome', 'predicted', 'protected'] + ['f{}'.format(i) for i in range(num_columns)]

# P[outcome = 1 | x = 1] = 0.5, P[outcome = 1 | x = 0] = 0.5
def get_random_row():
  return [1 if random() < prob else 0] + [1 if random() < 0.5 else 0 for _ in range(num_columns + 1)]
  
def get_predictive_parity(predicted):
  prediction = predicted[0]
  actual = 1 if prediction == 1 and random() < (1 - epsilon) else 0
  predicted.insert(0, actual)
  return predicted

def get_fpr(predicted):
  prediction = predicted[0]
  actual = 1 if (prediction == 1) or (prediction == 0 and random() < epsilon) else 0
  predicted.insert(0, actual)
  return predicted

def get_disparate_mistreatment(predicted):
  prediction = predicted[0]
  actual = 1 if (prediction == 1 and random() < 1 - epsilon) or (prediction == 0 and random() < epsilon) else 0
  predicted.insert(0, actual)
  return predicted

# P[outcome = 1 | y = 1] = 0.8, P[outcome = 1 | y = 0] = 0.3, y is an unprotected attribute
# P[outcome = 1 | x = 1] = 0.5, P[outcome = 1 | x = 0] = 0.5, x is a protected attribute
def get_biased_by_nonprotected_row():
  row = get_random_row()
  if num_columns < 1:
    print("Pick a different row type or increase number of columns to something greater than 0.")
    exit()

  attribute = row[2]

  row[0] = 1 if (attribute and random() < prob0) or (not attribute and random() < prob1) else 0
  return row

def get_row():
  if row_type == 'random':
    return get_random_row()
  elif row_type == 'ok':
    return get_biased_by_nonprotected_row()
  else:
    print("Row type {} is invalid".format(row_type))
    exit()

def get_condition(row):
  if parity_type == 'ppv':
    return get_predictive_parity(row)
  elif parity_type == 'fpr':
    return get_fpr(row)
  elif parity_type == 'mis':
    return get_disparate_mistreatment(row)

def validate_args():
  if num_samples < 0:
    print("Need a positive number of samples.") and exit()

  if num_columns < 0:
    print("Need a positive number of columns.") and exit()

  if epsilon > 0.5:
    print("Pick a meaningful epsilon less than 0.5.") and exit()

  # if row_type == 'random':
  #   print("Generating random rows...")
  # elif row_type == 'ok':
  #   print("Generating rows biased on an unprotected attribute...")
  # else:
  #   print("Row type {} is invalid".format(row_type))
  #   exit()

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  num_columns = args.columns
  num_samples = args.samples
  row_type = args.row
  parity_type = args.parity_type
  epsilon = args.epsilon

  prob = args.probability

  # For ok bias
  prob0 = args.prob0
  prob1 = args.prob1

  validate_args()

  filename = '{}/{}.csv'.format(directory, row_type)

  # if row_type == 'random':
  #   print("Using probability {} and epsilon {}".format(str(prob), str(epsilon)))
  # elif row_type == 'ok':
  #   print("Using probability {} and {} and epsilon {}".format(str(prob0), str(prob1), str(epsilon)))

  with open(filename, 'w') as f:
    column_names = get_cols(num_columns)
    f.write(','.join(column_names) + '\n')
    for _ in range(num_samples):
      row = get_row()
      actual_row = get_condition(row)
      f.write(','.join([str(i) for i in actual_row]) + '\n')

