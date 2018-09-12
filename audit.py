import argparse
import csv
import numpy as np
import os.path
import pandas as pd
import statistical_parity_generator as spg

from fairml import audit_model
from fairml import plot_dependencies
from multiprocessing import Pool
from sklearn.linear_model import LogisticRegression

parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='output directory')
parser.add_argument('--settings', '-s', type=str, default='settings.csv', help='file path for experiment settings')
parser.add_argument('--runs', '-r', type=int, default=100, help='number of trials')
parser.add_argument('--threads', '-t', type=int, default=10, help='number of threads')

def get_repr(value):
  return np.median(np.array(value))

def run(settings):
  # Extract Settings
  experiment = settings['title']
  m = int(settings['columns'])
  n = int(settings['samples'])
  biased = False if settings['biased'] == 'False' else True
  eps = float(settings['epsilon'])
  p_y_A = float(settings['proby'])
  p_a = float(settings['proba'])
  p = float(settings['prob'])

  output_filename = "{}/{}_output.csv".format(directory, experiment)

  # Keep record of data
  with open(output_filename, 'w') as f:
    column_names = ['X{}'.format(str(i)) for i in range(m)] + ['A']
    f.write(','.join(column_names) + '\n')

    for _ in range(num_trials):
      # Generate Dataset
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

      f.write(','.join([str(get_repr(importancies[i])) for i in column_names]) + '\n')

  # Log in overall experiment
  exp_name, exp_trial = experiment.split("-")
  results = pd.read_csv(output_filename)
  results_filename = "{}/{}_results.csv".format(directory, exp_name)

  results = results.abs()
  results['max'] = results.idxmax(axis=1)

  param = settings['parameter']

  results_columns = [param, 'FP']
  fp_count = results[results['max'] == 'A'].count()['A']

  write_header = False
  if not os.path.exists(results_filename):
    write_header = True
  results_file = open(results_filename, "a")

  if write_header:
    results_file.write(','.join(results_columns) + '\n')

  results_file.write(','.join([settings[param], str(fp_count)]) + '\n')

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  settings_filename = args.settings
  num_trials = int(args.runs)
  num_threads = int(args.threads)

  all_experiments = csv.DictReader(open(settings_filename))

  pool = Pool(num_threads)
  pool.map(run, all_experiments)
  pool.close() 
  pool.join()

