import numpy as np
import pandas as pd
import argparse
from random import randint

pp_file = "./data/propublica_data_for_fairml.csv"
out_file = "./data/propublica_attack_data.csv"


parser = argparse.ArgumentParser()
parser.add_argument('--epsilon', '-e', type=float, default=0, help='extra data for adversary to add')
parser.add_argument('--correlates', '-c', type=int, default=2, help='how many random correlates')

# Generate normally distributed correlates w/ some degree of noise
# Centered around effect of race (0.5) * race value -- i think r_effect is a magic number
# Spread is 0.5 -- not sure why he picked this?
def get_correlates_normal(num_correlates, race):
    return np.random.normal(r_effect * race, 0.2, (num_correlates,)).tolist()

def str_join(l):
    return ','.join([str(e) for e in l])

if __name__ == '__main__':
    r_effect = 0.5

    args = parser.parse_args()
    print(args)
    pp_data = pd.read_csv(pp_file)
    # print(pp_data.columns)
    new_row = []
    new_row_black = []
    for col in pp_data.columns.values:
        if col in {'score_factor', 'Age_Below_TwentyFive'}:
            new_row.append(1)
            new_row_black.append(1)
        else:
            new_row.append(0)
            new_row_black.append(0)
    new_row += [1] * args.correlates
    new_row_black += [0] * args.correlates
    cor_data = []
    r_index = pp_data.columns.get_loc('African_American')
    priors_index = pp_data.columns.get_loc('Number_of_Priors')
    all_correlates = []
    for line in pp_data.values:
        race = line[r_index]
        all_correlates.append(get_correlates_normal(args.correlates, race))
    with open(out_file, 'w') as outf:
        outf.write(str_join(pp_data.columns.values))
        if args.correlates > 0:
            outf.write(',' + str_join(['f' + str(i) for i in range(args.correlates)]))
        outf.write('\n')
        for data, cors in zip(pp_data.values, all_correlates):
            if len(cors) > 0:
                combined = str_join(data) + ',' + str_join(cors) + '\n'
            else:
                combined = str_join(data) + '\n'
            outf.write(combined)
        for _ in range(int(args.epsilon * pp_data.shape[0])):
            outf.write(str_join(new_row_black) + '\n')
            new_row[r_index] = 1
        for _ in range(int(args.epsilon * pp_data.shape[0])):
            # new_row[priors_index] = 20 + randint(-5, 10)
            new_row[r_index] = 0
            outf.write(str_join(new_row) + '\n')
