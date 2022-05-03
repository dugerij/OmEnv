#!/usr/bin/env

import falcon
import joblib
from .predict import PredictResource, GenerateCreditScore

app = application = falcon.App()

def load_trained_model():
    global model
    file = open('/Users/dugerij/Documents/Practice/APi/API/Models/Xgb_model.joblib.dat', 'rb')
    model = joblib.load(file)
    file.close()
    return model
def load_card():
    global card
    file = open('/Users/dugerij/Documents/Practice/APi/API/Scorecard/card', 'rb')
    card = joblib.load(file)
    file.close()
    return card

predict = PredictResource(model=load_trained_model())
score = GenerateCreditScore(card = load_card())
app.add_route('/predict', predict)
app.add_route('/creditscore', score)