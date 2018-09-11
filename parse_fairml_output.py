import argparse
import os.path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='File path for csv to be parsed')
parser.add_argument('--row', '-r', type=str, help='row type [random, ok]')
parser.add_argument('--file', '-f', type=str)
if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  row_type = args.row
  file_prefix = args.file

  input_filename = "{}/{}_{}_output.csv".format(directory, file_prefix, row_type)

  print(file_prefix)
  variables = file_prefix.split("-")
  print(variables)

  df = pd.read_csv(input_filename)
  output_filename = "{}/{}_audit_result.csv".format(directory, row_type)
  # variables = [
  #   file_prefix,
  #   str(round(df['correlation'].mean(), 1)),
  #   str(round(df['corr_conf'].mean(), 2)),
  #   str(round(df['protected_correlation'].mean(), 1)),
  #   str(round(df['pro_corr_conf'].mean(), 2)),
  #   str(round(df["accuracy"].mean(), 3))
  # ]
  df = df.abs()
  df['max'] = df.idxmax(axis=1)
#   output_filename = "{}/{}_audit_result.txt".format(directory, row_type)

#   with open(output_filename, 'w') as f:
#     f.write(str(df) + '\n\n\n')
#     f.write('Num. FP: ' + str(df[df['max'] == 'protected'].count()['protected']))
  variables.extend([
    str(round(df['accuracy'].mean(), 3)),
    str(df[df['max'] == 'protected'].count()['protected'])
  ])
  # str(df[abs(df['f0']) < abs(df['protected'])].count()['protected']/100.0)

  write_header = False
  if not os.path.exists(output_filename):
    write_header = True
  output_file = open(output_filename, "a")

  if write_header:
    if row_type == 'corr':
      output_file.write('corr,accuracy,FP\n')
    # if row_type == 'random':
    #   output_file.write('p,corr,corr_conf,protected,protected_conf,accuracy,FP\n')
    # elif len(variables) > 4:
    #   output_file.write(','.join(["p0", "p1", "c", "accuracy", "FP"])+ '\n')
    # elif len(variables) > 3:
    #   output_file.write(','.join(["p0", "p1", "accuracy", "FP"])+ '\n')
    else:
      output_file.write(','.join(["p", "c", "accuracy", "FP"])+ '\n')
  print(variables)
  output_file.write(','.join(variables) + '\n')
