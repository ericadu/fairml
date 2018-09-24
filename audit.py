import argparse
import csv
import numpy as np
import os.path
import pandas as pd
import statistical_parity_generator as spg
import counterfactual_generator as cg
import counterfactual_statistical_parity_generator as csg

from fairml import audit_model
from fairml import plot_dependencies
from multiprocessing import Pool
from sklearn.linear_model import LogisticRegression

# Pre-req: must create directory with subdirectories output and results
parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='output directory')
parser.add_argument('--settings', '-s', type=str, default='settings.csv', help='file path for experiment settings')
parser.add_argument('--runs', '-r', type=int, default=100, help='number of trials')
parser.add_argument('--threads', '-t', type=int, default=10, help='number of threads')
parser.add_argument('--property', '-p', type=str, help='[sp,cf,cfsp] -- statistical_parity, counterfactual')

def get_repr(value):
  return np.median(np.array(value))

def run(settings):
  # Extract Settings
  exp = settings['title']
  m = int(settings['columns'])
  n = int(settings['samples'])
  biased = False if settings['biased'] == 'False' else True
  delta = float(settings['delta'])
  eps = float(settings['epsilon'])
  # p_y_A = float(settings['proby'])
  # p_a = float(settings['proba'])
  p = float(settings['p'])

  output_filename = "{}/output/{}_output.csv".format(directory, exp)
  validation_filename = "{}/validation/{}.csv".format(directory, exp)
  vf = open(validation_filename, "a")
  # vf.write('m,n,eps,p_y_A,p_a,p_biased,p_unbiased,x_corr,a_corr\n')
  vf.write('m,n,delta,eps,p\n')

  # Keep record of data
  with open(output_filename, 'w') as f:
    column_names = ['X{}'.format(str(i)) for i in range(m)] + ['A']
    # f.write(','.join(column_names + ['checked']) + '\n')
    f.write(','.join(column_names) + '\n')

    for _ in range(num_trials):
      # Generate Dataset
      # df = spg.generate_dataset(exp, m, n, biased, eps, p_y_A, p_a, p)
      # validated = spg.validate_dataset(df)
      #df = csg.generate_dataset(m, n, biased, eps, delta, p)
      df = cg.generate_dataset(m, n, biased, delta, p)
      validated = cg.validate_dataset(df, biased)
      # checked = check_settings([m, n, eps, p_y_A, p_a, p, biased], validated)
      vf.write(','.join([str(round(i, 4)) for i in validated]) + '\n')

      output = df.O.values
      df = df.drop("O", 1)

      #  quick setup of Logistic regression
      #  perhaps use a more crazy classifier
      clf = LogisticRegression(penalty='l2', C=0.01)
      clf.fit(df.values, output)
      #  call audit model
      importancies, _ = audit_model(clf.predict, df)

      # f.write(','.join([str(get_repr(importancies[i])) for i in column_names] + [str(checked)]) + '\n')
      f.write(','.join([str(get_repr(importancies[i])) for i in column_names]) + '\n')
  results = pd.read_csv(output_filename)
  exp_name, exp_trial = exp.split("-")
  results_filename = "{}/results/{}_results.csv".format(directory, exp_name)
  # validation_results_filename = "{}/results/validation.csv".format(directory, exp_name)

  # Log in overall experiment
  # if True in results.checked.values:
  #   checked_true = results.checked.value_counts()[True]
  # else:
  #   checked_true = 0

  # vrf = open(validation_results_filename, "a")
  # vrf.write("{},{}\n".format(exp, str(checked_true / float(num_trials))))

  # results = results.drop("checked", 1)
  results = results.abs()
  results['max'] = results.idxmax(axis=1)

  results_columns = ['delta', 'eps', 'FP']
  # param = settings['parameter']
  # results_columns = [param, 'FP']
  fp_count = results[results['max'] == 'A'].count()['A']

  write_header = False
  if not os.path.exists(results_filename):
    write_header = True
  results_file = open(results_filename, "a")

  if write_header:
    results_file.write(','.join(results_columns) + '\n')

  results_file.write(','.join([str(delta), str(eps), str(fp_count)]) + '\n')
  # results_file.write(','.join([settings[param], str(fp_count)]) + '\n')

def check_settings(expected, actual):
  p_biased, p_unbiased = actual[5:7]

  biased = expected[-1]
  p = p_biased if biased == True else p_unbiased
  x_corr, a_corr = actual[7:]

  expected_values = [round(i, 1) for i in expected[:6]]
  actual_values = [round(i, 1) for i in list(actual[:5]) + [p]]

  if expected_values != actual_values:
    return False

  if (biased and p_biased != 0.5 and round(x_corr, 1) == 0) or (not biased and round(x_corr, 1) != 0):
      return False

  return True

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

