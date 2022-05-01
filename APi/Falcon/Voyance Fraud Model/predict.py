import os
import joblib
import pandas as pd
import random
import scorecardpy as sc
from credit_scorecard import card_path

random.seed(3)

card = pd.read_pickle(card_path)

model_filename = os.path.join('model.dat')
model = joblib.load(model_filename)

def predict(X_test, card):

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    score = sc.scorecard_ply(X_test, card, only_total_score=True, print_step=0, replace_blank_na=True, var_kp = None)
    return y_pred, score

