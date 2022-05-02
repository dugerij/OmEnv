import os
import falcon
import joblib
import scorecardpy as sc
from .predict import PredictResource, GenerateCreditScore

api = application = falcon.API()


def load_trained_model():
    global model
    model = joblib.load('Xgb_model.joblib')
    return model
def load_card():
    global card 
    card = joblib.load('card')
    return card

predict = PredictResource(model=load_trained_model())
score = GenerateCreditScore(card = load_card())
api.add_route('/predict', predict)
api.add_route('/creditscore', score)