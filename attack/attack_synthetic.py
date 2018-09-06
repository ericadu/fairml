import matplotlib

# temporary work around down to virtualenv
# matplotlib issue.
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from sklearn.linear_model import LogisticRegression

# import specific projection format.
from fairml import audit_model
from fairml import plot_dependencies

plt.style.use('ggplot')
plt.figure(figsize=(6, 6))

# read in propublica data
attack_data = pd.read_csv("./data/attack_data.csv")

# quick data processing
scores = attack_data.score.values
attack_data = attack_data.drop("score", 1)
attack_data = attack_data.drop("outcome", 1)

#  quick setup of Logistic regression
#  perhaps use a more crazy classifier
clf = LogisticRegression(penalty='l2', C=0.01)
clf.fit(attack_data.values, scores)
# print("new model coefficients: %s" % str(clf.coef_))
# print(attack_data.axes[1])

#  call audit model
importancies, _ = audit_model(lambda x: clf.predict_proba(x)[:,1], attack_data)

# print feature importance
print(np.median(importancies['race']))

# generate feature dependence plot
fig = plot_dependencies(
    importancies.median(),
    reverse_values=False,
    title="FairML feature dependence logistic regression model"
)

file_name = "./output/fairml_attack.png"
plt.savefig(file_name, transparent=False, bbox_inches='tight', dpi=250)

