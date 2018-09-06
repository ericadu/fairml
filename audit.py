import matplotlib

# temporary work around down to virtualenv
# matplotlib issue.
matplotlib.use('Agg')
import numpy as np
import os.path
import matplotlib.pyplot as plt
import argparse

import pandas as pd
from sklearn.linear_model import LogisticRegression

# import specific projection format.
from fairml import audit_model
from fairml import plot_dependencies

parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='output directory')
parser.add_argument('--row', '-r', type=str, default='random', help='Row type. [random, ok]')
parser.add_argument('--columns', '-c', type=int, default=1, help='number of extra columns. needs to be greater than or equal to 0')

def get_cols():
  return ['f{}'.format(i) for i in range(num_columns)] + ['protected']

def get_col_values(column_names):
  return [str(get_repr(i)) for i in column_names]


def get_repr(value):
  return np.median(np.array(importancies[value]))

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  row_type = args.row
  num_columns = args.columns

  # plt.style.use('ggplot')
  # plt.figure(figsize=(6, 6))

  input_filename = "{}/{}.csv".format(directory, row_type)
  input_data = pd.read_csv(input_filename)

  # quick data processing
  output = input_data.outcome.values
  input_data = input_data.drop("outcome", 1)
  if "predicted" in input_data.columns:
    input_data = input_data.drop("predicted", 1)

  #  quick setup of Logistic regression
  #  perhaps use a more crazy classifier
  clf = LogisticRegression(penalty='l2', C=0.01)
  clf.fit(input_data.values, output)
  #  call audit model
  importancies, _ = audit_model(clf.predict, input_data)

  # print feature importance
  # print("Relative Rankings:")
  # print(importancies)
  # print("\n")

  output_filename = "{}/{}_output.csv".format(directory, row_type)
  write_header = False

  if not os.path.exists(output_filename):
    write_header = True

  output_file = open(output_filename, "a")
  column_names = get_cols()
  if write_header:
    output_file.write(','.join(column_names) + '\n')
  output_file.write(','.join(get_col_values(column_names)) + '\n')

  # generate feature dependence plot
  # fig = plot_dependencies(
  #     importancies.median(),
  #     reverse_values=False,
  #     title="FairML feature dependence logistic regression model"
  # )

  # file_name = "fairml_linear_direct_{}.png".format(row_type)
  # plt.savefig(file_name, transparent=False, bbox_inches='tight', dpi=250)
