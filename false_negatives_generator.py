import sys
import os.path
import numpy as np
from random import random
import argparse
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from scipy import stats

# import specific projection format.
from fairml import audit_model

parser = argparse.ArgumentParser()
parser.add_argument('--columns', '-c', type=int, default=1, help='number of extra columns. needs to be greater than or equal to 0')
parser.add_argument('--samples', '-s', type=int, default=10000, help='number of samples')
parser.add_argument('--row', '-r', type=str, default='random', help='what type of row. select from the following list [random, ok, corr]')
parser.add_argument('--epsilon', '-e', type=float, default=0.1, help='epsilon statistical parity')
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='output folder')
parser.add_argument('--probability', '-p', type=float, default=0.5, help='probability variable or pearsons coeff')
parser.add_argument('--prob0', type=float, default=1.0)
parser.add_argument('--prob1', type=float, default=0.0)

def get_col_values(column_names):
  return [str(get_repr(i)) for i in column_names]

def get_repr(value):
  return np.median(np.array(importancies[value]))

# P[outcome = 1 | x = 1] = 0.5, P[outcome = 1 | x = 0] = 0.5
def check_statistical_parity(data):
  group_by_protected = data.groupby(['protected', 'outcome']).size()
  total_absent = data.protected.value_counts()[0]
  total_present = data.protected.value_counts()[1]

  p_positive_absent = float(group_by_protected[0][1]) / total_absent
  p_positive_present = float(group_by_protected[1][1]) / total_present
  eps = abs(p_positive_absent - p_positive_present)

  if eps < epsilon:
    #print("Satisfies statistical parity, epsilon = {}".format(str(eps)))
    return (True, eps)
  else:
    #print("Generating a different dataset, epsilon = {}.".format(str(eps)))
    #print("Violates statistical parity at eps = {}.".format(str(eps)))
    return (False, eps)

def get_cols():
  return ['outcome', 'protected'] + ['f{}'.format(i) for i in range(num_columns)]

def get_random_row():
  return [1 if random() < prob else 0] + [1 if random() < 0.5 else 0 for _ in range(num_columns + 1)]

def get_fn_row():
  row = get_random_row()
  row[1] = 1 if random() < prob else 0
  if row[1] == 1:
    row[0] = 1 if random() < prob0 else 0
  else:
    row[0] = 1 if random() < prob1 else 0
  return row

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  num_columns = args.columns
  num_samples = args.samples
  row_type = args.row
  epsilon = args.epsilon
  prob = args.probability
  prob0 = args.prob0
  prob1 = args.prob1

  input_data = np.zeros((num_samples, num_columns + 2)) 
  test_data = np.zeros((num_samples, num_columns + 2)) 
  column_names = get_cols()

  satisfies = True
  while satisfies:
    for i in range(num_samples):
      input_data[i,:] = get_fn_row()
      test_data[i,:] = get_fn_row()

    input_df = pd.DataFrame(data=input_data, index=range(0,num_samples),columns=column_names)
    test_df = pd.DataFrame(data=test_data, index=range(0,num_samples),columns=column_names)
    satisfies, eps = check_statistical_parity(input_df)
    pearsons = stats.pearsonr(input_df.f0.values, input_df.outcome.values)
    pearsons_protected = stats.pearsonr(input_df.protected.values, input_df.outcome.values)
    #print("pearsons correation: {}".format(pearsons))

  input_outcome= input_df.outcome.values
  input_df = input_df.drop("outcome", 1)
  if "predicted" in input_df.columns:
    input_df = input_df.drop("predicted", 1)

  #  quick setup of Logistic regression
  clf = LogisticRegression(penalty='l2', C=0.01)

  clf.fit(input_df.values, input_outcome)

  test_outcome = test_df.outcome.values
  test_df = test_df.drop("outcome", 1)
  predicted = clf.predict(test_df)
  accuracy = accuracy_score(test_outcome, predicted)
  #  call audit model
  importancies, _ = audit_model(clf.predict, input_df)

  if num_columns > 1:
    output_filename = "{}/{}-{}_{}_output.csv".format(directory, prob0, num_columns, row_type)
  else:
    #output_filename = "{}/{}_{}_output.csv".format(directory, prob, row_type)
    output_filename = "{}/{}-{}-{}_output.csv".format(directory, prob, prob0, prob1)

  write_header = False
  if not os.path.exists(output_filename):
    write_header = True

  output_file = open(output_filename, "a")
  output_column_names = get_cols()[1:]
  output_column_values = get_col_values(output_column_names)

  extra_column_names = ['accuracy', 'eps', 'protected_corr', 'pcp', 'fcorr', 'fcp']
  extra_column_values = [str(accuracy),
    str(round(eps, 2)),
    str(round(pearsons_protected[0], 2)),
    str(round(pearsons_protected[1], 2)),
    str(round(pearsons[0], 2)),
    str(round(pearsons[1], 2))
  ]

  output_column_values.extend(extra_column_values)
  output_column_names.extend(extra_column_names)

  if write_header:
    output_file.write(','.join(output_column_names) + '\n')
  output_file.write(','.join(output_column_values) + '\n')







