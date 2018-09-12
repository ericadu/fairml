import matplotlib

# temporary work around down to virtualenv
# matplotlib issue.
matplotlib.use('Agg')
import numpy as np
import os.path
import matplotlib.pyplot as plt
import argparse
import statistical_parity_generator as spg

import pandas as pd
from sklearn.linear_model import LogisticRegression

# import specific projection format.
from fairml import audit_model
from fairml import plot_dependencies

parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='output directory')
parser.add_argument('--title', '-t', type=str, help='experiment title')
parser.add_argument('--columns', '-m', type=int, default=1, help='number of extra columns. needs to be greater than or equal to 1')
parser.add_argument('--samples', '-n', type=int, default=10000, help='number of samples')
parser.add_argument('--biased', '-b', help='biased or unbiased', action="store_true")
parser.add_argument('--epsilon', '-e', type=float, default=0.0, help='epsilon')
parser.add_argument('--proby', '-y', type=float, default=0.5, help='p_y_A')
parser.add_argument('--proba', '-a', type=float, default=0.5, help='p_a')
parser.add_argument('--prob', '-p', type=float, default=0.5, help='p')

def get_repr(value):
  return np.median(np.array(importancies[value]))

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  experiment = args.experiment
  biased = args.biased
  m = args.columns
  n = args.samples
  eps = args.epsilon
  p_y_A = args.proby
  p_a = args.proba
  p = args.prob

  if biased:
    p = (1 + p) / 2

  dataset = spg.generate_dataset(m, n, biased, eps, p_y_A, p_a, p)
  columns = ['X{}'.format(str(i)) for i in range(m)] + ['A', 'O']
  # quick data processing

  df = pd.DataFrame(data=dataset, columns=columns)
  output = df.O.values
  df = df.drop("O", 1)

  #  quick setup of Logistic regression
  #  perhaps use a more crazy classifier
  clf = LogisticRegression(penalty='l2', C=0.01)
  clf.fit(df.values, output)
  #  call audit model
  importancies, _ = audit_model(clf.predict, df)


  output_filename = "{}/{}_output.csv".format(directory, experiment)
  write_header = False

  if not os.path.exists(output_filename):
    write_header = True

  output_file = open(output_filename, "a")

  columns.pop()
  if write_header:
    output_file.write(','.join(columns) + '\n')

  output_file.write(','.join([str(get_repr(i)) for i in columns]) + '\n')

