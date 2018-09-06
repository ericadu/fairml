import os.path
import pandas as pd

dir_name = 'data/generator/statistical_parity'

# df0 = pd.read_csv('{}/accuracy-0/ok_audit_result.csv'.format(dir_name))
# df1 = pd.read_csv('{}/accuracy-1/ok_audit_result.csv'.format(dir_name))
# df2 = pd.read_csv('{}/accuracy-2/ok_audit_result.csv'.format(dir_name))
# df3 = pd.read_csv('{}/accuracy-3/ok_audit_result.csv'.format(dir_name))
# df4 = pd.read_csv('{}/accuracy-4/ok_audit_result.csv'.format(dir_name))

# df = pd.concat([df0, df1, df2, df3])
df = pd.read_csv('{}/accuracy-5/ok_audit_result.csv'.format(dir_name))

# df_rand['fraction'] = df_rand['FP']/100.0

# grouped = df_rand.groupby(['p'])
# for p, group in grouped:
#   fp = round(group.mean()['fraction'], 3)
#   print("{} & {} \\\\".format(p, fp))
grouped = df.groupby(['p0', 'p1'])

current = None
count = 0
string = ""
for name, group in grouped:
  p0, p1 = name
  fp = round(group.mean()['FP'], 3)
  if current == p0:
    count += 1
  else:
    count = 1
    current = p0
    string = "& {} &".format(p0)
  string += " {} ".format(fp)
  if count == 9:
    string += "\\\\"
    print(string)
    string = ""
  else:
    string += "&"
