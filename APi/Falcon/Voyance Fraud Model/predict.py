import os
import pickle
import pandas as pd
import random
import sklearn

random.seed(3)

def predict(X_test):
    model_filename = os.path.join('model.dat')
    model = pickle.load(open(model_filename, 'rb'))
    Species_class_map = {0: 'Iris-setosa', 1: }

    y_pred = model.predict(X_test)
    y_pred = [round(value) for value in y_pred]
    prediction_result = ['Species': Species_class_map[y_pred[0]]]
    return prediction_result

