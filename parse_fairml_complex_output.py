import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--directory', '-d', type=str, default='data/generator/statistical_parity', help='File path for csv to be parsed')
parser.add_argument('--row', '-r', type=str, help='row type [random, ok]')

if __name__ == '__main__':
  args = parser.parse_args()
  directory = args.directory
  row_type = args.row
  input_filename = "{}/{}_output.csv".format(directory, row_type)

  df = pd.read_csv(input_filename)
  df = df.abs()
  df['max'] = df.idxmax(axis=1)
  output_filename = "{}/{}_audit_result.txt".format(directory, row_type)

  with open(output_filename, 'w') as f:
    f.write(str(df) + '\n\n\n')
    f.write('Num. FP: ' + str(df[df['max'] == 'protected'].count()['protected']))
    # f.write("False Positives:\n")
    # f.write(str(df[df['max'] == 'protected'].describe()))
    # f.write("\n\nEqual weight:\n")
    # f.write(str(df[abs(df['f0']) == abs(df['protected'])].describe()))
    # f.write("\n\nf0 has more weight:\n")
    # f.write(str(df[abs(df['f0']) > abs(df['protected'])].describe()))