from sklearn.linear_model import LogisticRegression
import argparse
import numpy as np
import json

parser = argparse.ArgumentParser()
parser.add_argument('--filename', '-f', type=str, help='filename of test dataset')

if __name__ == '__main__':
  args = parser.parse_args()
  filename = args.filename
  loaded_clf = json.load(open(filename))

  clf = LogisticRegression()
  for k, v in loaded_clf.items():
      if isinstance(v, list):
          setattr(clf, k, np.matrix(v))
      else:
          setattr(clf, k, v)

  print(clf.__dict__)

