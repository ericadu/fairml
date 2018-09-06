import sys
import os.path
import numpy as np
from random import random
import argparse
import pandas as pd
from sklearn.svm import SVC
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
parser.add_argument('--prob0', type=float, default=0.0)
parser.add_argument('--prob1', type=float, default=0.0)
parser.add_argument('--algorithm', '-a', type=str, default='logr', help='[logr,svm]')

def get_cols():
  return ['outcome', 'protected'] + ['f{}'.format(i) for i in range(num_columns)]

def get_col_values(column_names):
  return [str(get_repr(i)) for i in column_names]

def get_repr(value):
  return np.median(np.array(importancies[value]))

# P[outcome = 1 | x = 1] = 0.5, P[outcome = 1 | x = 0] = 0.5
def get_random_row():
  return [1 if random() < prob else 0] + [1 if random() < 0.5 else 0 for _ in range(num_columns + 1)]

# P[outcome = 1 | y = 1] = 0.8, P[outcome = 1 | y = 0] = 0.3, y is an unprotected attribute
# P[outcome = 1 | x = 1] = 0.5, P[outcome = 1 | x = 0] = 0.5, x is a protected attribute
def get_biased_by_nonprotected_row():
  row = get_random_row()
  if num_columns < 1:
    print("Pick a different row type or increase number of columns to something greater than 0.")
    exit()

  attribute = row[2]

  p = random()
  if attribute and p < prob0:
    row[0] = 1
  elif (not attribute) and p < prob1:
    row[0] = 1
  else:
    row[0] = 0

  #row[0] = 1 if (attribute and random() < prob0) or (not attribute and random() < prob1) else 0
  return row

def get_corr_row():
  row = get_random_row()
  if num_columns < 1:
    print("Pick a different row type or increase number of columns to something greater than 0.")
    exit()
  attribute = row[2]

  p = random()
  flipped = 0 if attribute == 1 else 1
  if p < prob:
    row[0] = attribute
  else:
    row[0] = flipped
  return row


def check_statistical_parity(data):
  group_by_protected = data.groupby(['protected', 'outcome']).size()
  total_absent = data.protected.value_counts()[0]
  total_present = data.protected.value_counts()[1]

  p_positive_absent = float(group_by_protected[0][1]) / total_absent
  p_positive_present = float(group_by_protected[1][1]) / total_present
  eps = abs(p_positive_absent - p_positive_present)

  if eps < epsilon:
    #print("Satisfies statistical parity, epsilon = {}".format(str(eps)))
    return True
  else:
    #print("Generating a different dataset, epsilon = {}.".format(str(eps)))
    return False

def get_row():
  if row_type == 'random':
    return get_random_row()
  elif row_type == 'ok':
    return get_biased_by_nonprotected_row()
  elif row_type == 'corr':
    return get_corr_row()
  else:
    print("Row type {} is invalid".format(row_type))
    exit()

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
  epsilon = args.epsilon
  prob = args.probability
  alg = args.algorithm

  # For ok bias
  prob0 = args.prob0
  prob1 = args.prob1

  # For corr
  correlation = 0
  protected_correlation = 0

  validate_args()
  # filename = '{}/{}.csv'.format(directory, row_type)

  # if row_type == 'random':
  #   print("Using probability {}".format(str(prob)))
  # elif row_type == 'ok':
  #   print("Using probability {} and {}".format(str(prob0), str(prob1)))

  # with open(filename, 'w') as f:
  #   column_names = get_cols(num_columns)
  #   f.write(','.join(column_names) + '\n')
  #   for _ in range(num_samples):
  #     row = get_row()
  #     f.write(','.join([str(i) for i in row]) + '\n')

  input_data = np.zeros((num_samples, num_columns + 2)) 
  test_data = np.zeros((num_samples, num_columns + 2)) 
  column_names = get_cols()

  satisfies = False
  while not satisfies:
    for i in range(num_samples):
      input_data[i,:] = get_row()
      test_data[i,:] = get_row()
    
    # Input dataframe
    input_df = pd.DataFrame(data=input_data, index=range(0,num_samples),columns=column_names)
    test_df = pd.DataFrame(data=test_data, index=range(0,num_samples),columns=column_names)

    satisfies = check_statistical_parity(input_df)
    #satisfies = True
    # pearsons = stats.pearsonr(input_df.f0.values, input_df.outcome.values)
    # pearsons_protected = stats.pearsonr(input_df.protected.values, input_df.outcome.values)

    # if row_type == 'corr':
    #   if pearsons[1] < 0.05:
    #     correlation = pearsons[0]
    #   else:
    #     satisfies = False

  # quick data processing
  input_outcome= input_df.outcome.values
  input_df = input_df.drop("outcome", 1)
  if "predicted" in input_df.columns:
    input_df = input_df.drop("predicted", 1)

  #  quick setup of Logistic regression
  if alg == 'logr':
    clf = LogisticRegression(penalty='l2', C=0.01)
  else:
    clf = SVC(C=0.01)

  clf.fit(input_df.values, input_outcome)

  test_outcome = test_df.outcome.values
  test_df = test_df.drop("outcome", 1)
  predicted = clf.predict(test_df)
  accuracy = accuracy_score(test_outcome, predicted)
  #  call audit model
  importancies, _ = audit_model(clf.predict, input_df)

  if num_columns > 1:
    output_filename = "{}/{}-{}_{}_output.csv".format(directory, prob0, num_columns, row_type)
  elif prob0 and prob1:
    output_filename = "{}/{}-{}_{}_output.csv".format(directory, prob0, prob1, row_type)
  else:
    output_filename = "{}/{}_{}_{}_output.csv".format(directory, alg, prob, row_type)

  write_header = False
  if not os.path.exists(output_filename):
    write_header = True

  output_file = open(output_filename, "a")
  output_column_names = get_cols()[1:]
  output_column_values = get_col_values(output_column_names)

  extra_column_names = ['accuracy']
  extra_column_values = [str(accuracy)]

  if num_columns > 1:
    extra_column_names.append('c')
    extra_column_values.append(str(num_columns))
  #extra_columns = [str(accuracy), str(round(pearsons[0], 2)), str(round(pearsons[1], 2)), str(round(pearsons_protected[0], 2)), str(round(pearsons_protected[1], 2))]
  # output_column_values.append(str(accuracy))
  # output_column_values.append(str(round(correlation, 2)))
  # output_column_values.append(str(round(protected_correlation, 2)))
  output_column_values.extend(extra_column_values)
  output_column_names.extend(extra_column_names)
  # , 'correlation', 'corr_conf', 'protected_correlation', 'pro_corr_conf'
    

  if write_header:
    output_file.write(','.join(output_column_names) + '\n')
  output_file.write(','.join(output_column_values) + '\n')
