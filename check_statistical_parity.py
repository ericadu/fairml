import pandas as pd

data = pd.read_csv("./data/complex_test.csv")
# group_by_positive_outcome = data.groupby(['outcome', 'gender']).size()[1]
# print(group_by_positive_outcome)
group_by_gender = data.groupby(['gender', 'outcome']).size()
total_men = data.gender.value_counts()[0]
total_women = data.gender.value_counts()[1]
# total_positive_outcomes = data.outcome.value_counts()[1]
# gender_0 = group_by_positive_outcome[0] / total_positive_outcomes
# gender_1 = group_by_positive_outcome[1] / total_positive_outcomes
p_positive_men = group_by_gender[0][1] / total_men
p_positive_women = group_by_gender[1][1] / total_women
epsilon = abs(p_positive_men - p_positive_women)
if epsilon < 0.01:
  print("Satisfies statistical parity, epsilon = {}".format(str(epsilon)))
else:
  print("Generate a different dataset, epsilon = {}.".format(str(epsilon)))