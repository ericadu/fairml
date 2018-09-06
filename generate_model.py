from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib
# temporary work around down to virtualenv
# matplotlib issue.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import numpy as np
from random import random
import argparse
import pandas as pd
from fairml import audit_model
from fairml import plot_dependencies
import json

parser = argparse.ArgumentParser()
parser.add_argument('--columns', '-c', type=int, default=3, help='number of extra columns')
parser.add_argument('--samples', '-s', type=int, default=100000, help='number of samples')
parser.add_argument('--filename', '-f', type=str, help='filename of test dataset')
## Example Use: $ python3 generate_model.py -f "complex"

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
  married_row[0] = 1 if ((random() < 0.9 and married == 1) or (random() < 0.1 and married == 0)) else 0
  return married_row

# P[married | x = male] = 0.3, P[married | x = female] = 0.8
# P[outcome | x = male] = 0.5, P[outcome | x = unmarried female] = 0.8, P[outcome | x = married female] = 0.2
# gender = 1 for women
def get_complex_row():
  complex_row = get_random_row()
  gender = complex_row[1]
  married = complex_row[2]
  complex_row[2] = 1 if ((random() < 0.8 and gender == 1) or (random() < 0.3 and gender == 0)) else 0
  complex_row[0] = 1 if (random() < 0.5 and gender == 0) or (random() < 0.2 and gender == 1 and married == 1) or (random() < 0.8 and gender == 1 and married == 0) else 0
  return complex_row

# P[married | x = male] = 0.3, P[married | x = female] = 0.6
# P[outcome | x = male] = 0.3, P[outcome | x = unmarried female] = 0.9, P[outcome | x = married female] = 0.1
# gender = 1 for women
def get_non_sp_complex_row():
  complex_row = get_random_row()
  gender = complex_row[1]
  married = complex_row[2]
  complex_row[2] = 1 if ((random() < 0.8 and gender == 1) or (random() < 0.3 and gender == 0)) else 0
  complex_row[0] = 1 if (random() < 0.1 and gender == 0) or (random() < 0.1 and gender == 1 and married == 1) or (random() < 0.9 and gender == 1 and married == 0) else 0
  return complex_row

if __name__ == '__main__':
  args = parser.parse_args()
  num_columns = args.columns
  num_samples = args.samples
  filename = args.filename
  train_filename = "./data/model/{}_train.csv".format(filename)
  test_filename = "./data/model/{}_test.csv".format(filename)

  ## Train Model
  train_data = np.zeros((num_samples, num_columns + 3))
  print("Saving to: " + train_filename)
  with open(train_filename, 'w') as f:
    f.write(','.join(get_cols(num_columns)) + '\n')
    for i in range(num_samples):
      # TODO: CHANGE ROW TYPE
      train_row = get_non_sp_complex_row()
      train_data[i,:] = train_row
      f.write(','.join([str(i) for i in train_row]) + '\n')


  # Check to see if original dataset satisfies statistical parity
  train_data_check = pd.read_csv(train_filename)
  group_by_gender_train = train_data_check.groupby(['gender', 'outcome']).size()
  print(group_by_gender_train)
  train_total_men = train_data_check.gender.value_counts()[0]
  train_total_women = train_data_check.gender.value_counts()[1]
  train_p_positive_men = group_by_gender_train[0][1] / train_total_men
  train_p_positive_women = group_by_gender_train[1][1] / train_total_women
  train_epsilon = abs(train_p_positive_men - train_p_positive_women)
  if train_epsilon < 0.01:
    print("Training set satisfies statistical parity, epsilon = {}".format(str(train_epsilon)))
  else:
    print("Training set does not satisfy statistical parity, epsilon = {}.".format(str(train_epsilon)))

  clf = LogisticRegression(penalty='l2', C=0.01)
  clf.fit(train_data[:,1:], train_data[:,0])
  print(list(clf.coef_))

  ## Create Test dataset w/ same distribution, and input into model.
  print("Saving to: " + test_filename)
  with open(test_filename, 'w') as f:
    raw_test_data = np.zeros((num_samples, num_columns + 3))
    column_names = get_cols(num_columns)
    column_names.insert(1, "actual")
    f.write(','.join(column_names) + '\n')
    for d in raw_test_data:
      d = list(d)
      # TODO: CHANGE ROW TYPE
      row = get_non_sp_complex_row()
      row.insert(1 if random() < clf.predict_proba([d[1:]])[0,1] else 0, 0)
      f.write(','.join([str(i) for i in row]) + '\n')

  # Check that dataset satisfies statistical parity
  test_data = pd.read_csv(test_filename)
  group_by_gender = test_data.groupby(['gender', 'outcome']).size()
  print(group_by_gender)
  total_men = test_data.gender.value_counts()[0]
  total_women = test_data.gender.value_counts()[1]
  p_positive_men = group_by_gender[0][1] / total_men
  p_positive_women = group_by_gender[1][1] / total_women
  epsilon = abs(p_positive_men - p_positive_women)
  if epsilon < 0.01:
    print("Satisfies statistical parity, epsilon = {}".format(str(epsilon)))
  else:
    print("Does not satisfy statistical parity, epsilon = {}.".format(str(epsilon)))

  print("Accuracy score: " + str(accuracy_score(test_data.actual, test_data.outcome)))
  ## FairML Audit
  test_data = test_data.drop("outcome", 1)
  test_data = test_data.drop("actual", 1)
  importancies, _ = audit_model(clf.predict, test_data)

  # print feature importance
  print(importancies)

  # generate feature dependence plot
  fig = plot_dependencies(
    importancies.median(),
    reverse_values=False,
    title="FairML feature dependence logistic regression model"
  )

  file_name = "./data/model/{}_report.png".format(filename)
  plt.savefig(file_name, transparent=False, bbox_inches='tight', dpi=250)


  attr = clf.__dict__
  print(attr)
  for k, v in attr.items():
    if (type(v).__module__ == np.__name__):
        attr[k] = v.tolist()

  json.dump(attr, open('./data/model/{}_attributes.json'.format(filename), 'w'))

