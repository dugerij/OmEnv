#!/usr/bin/env

import json
import falcon
import numpy as np
import pandas as pd
import random
import scorecardpy as sc

import torch
import skorch
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
# import lightgbm
# from lightgbm import LGBMClassifier

random.seed(3)


X_test = {'customerId': 202109203271, 'personalDetails.typeOfID': 'PVC', 'personalDetails.gender': 'male', 'personalDetails.religion': 'Islam', 'personalDetails.maritalStatus': 'Married', 'personalDetails.numberOfChildren': 2.0, 'business.dailyIncome': '11000', 'business.type': 'Transport', 'business.weeklyMarketAttendance': 6.0, 'business.yearsInBusiness': 6.0, 'guarantor.typeOfID': 'PVC', 'guarantor.gender': 'male', 'guarantor.religion': 'Islam', 'guarantor.business.monthlyIncome': '50000-200000', 'guarantor.business.type': 'AUTOMOBILE MECHANIC', 'guarantor.business.yearsInBusiness': 6.0, 'Dibursement Date': '2021-10-06T16:20:07.611Z', 'Disbursed Amount': 210000.0, 'Repayment Start Date': '2021-10-11T16:20:06.178Z', 'Repayment End Date': '2021-11-02T16:20:06.178Z', 'Loan Balance': 0.0}

def process_event(raw_json):
    # input_dict = json.loads(raw_json.decode())
    # raw_json= {'customerId': 202109203271, 'personalDetails.typeOfID': 'PVC', 'personalDetails.gender': 'male', 'personalDetails.religion': 'Islam', 'personalDetails.maritalStatus': 'Married', 'personalDetails.numberOfChildren': 2.0, 'business.dailyIncome': '11000', 'business.type': 'Transport', 'business.weeklyMarketAttendance': 6.0, 'business.yearsInBusiness': 6.0, 'guarantor.typeOfID': 'PVC', 'guarantor.gender': 'male', 'guarantor.religion': 'Islam', 'guarantor.business.monthlyIncome': '50000-200000', 'guarantor.business.type': 'AUTOMOBILE MECHANIC', 'guarantor.business.yearsInBusiness': 6.0, 'Dibursement Date': '2021-10-06T16:20:07.611Z', 'Disbursed Amount': 210000.0, 'Repayment Start Date': '2021-10-11T16:20:06.178Z', 'Repayment End Date': '2021-11-02T16:20:06.178Z', 'Loan Balance': 0.0}
    X_test = raw_json
    X_test = pd.DataFrame(X_test, index=[0], columns=list(X_test.keys()))
    
    def date_columns_conv(df, column):
        today_date = (pd.to_datetime('2022-04-15', utc=True))
 
        df[column] = (pd.to_datetime(df[column], format='%Y-%m-%d'))
        df['mths_since_' + column] = round(pd.to_numeric((today_date - df[column]) / np.timedelta64(1, 'M')))
    
        df['mths_since_' + column] = df['mths_since_' + column].apply(lambda x: df['mths_since_' + column].max() if x<0 else x)
        df.drop(columns=[column], inplace=True)

    date_columns_conv(X_test, 'Dibursement Date')

    # We will drop future looking columns i.e  'Repayment Start Date', 'Repayment End Date' as well as 'Loan Balance' as it will have similar implications as 'Days Outstanding' 
    X_test.drop(columns=['Repayment Start Date', 'Repayment End Date', 'Loan Balance'], inplace=True)
    
    # Change daily income from object to numbers
    X_test['business.dailyIncome'] = pd.to_numeric(X_test['business.dailyIncome'])

    # 
    X_test.drop(columns=['customerId'], inplace=True)

    # Drop unhelpful columns gender and religion and business.type
    X_test.drop(columns=['personalDetails.gender', 'personalDetails.religion', 'business.type', 'guarantor.gender', 'guarantor.religion', 'guarantor.business.type'], inplace=True)

    cat_list = ['personalDetails.typeOfID', 'personalDetails.maritalStatus',
       'guarantor.typeOfID', 'guarantor.business.monthlyIncome']

    def dummy_creation(df, column_list):
        df_dummies = []
        for col in column_list:
            df_dummies.append(pd.get_dummies(df[col], prefix=col, prefix_sep='_'))
            df.drop(columns=col, inplace=True)
        df_dummies = pd.concat(df_dummies, axis=1)
        df = pd.concat([df, df_dummies], axis=1)
        
        return df

    X_test = dummy_creation(X_test, cat_list)
    

    expected_columns =[
        'personalDetails.numberOfChildren', 'business.dailyIncome', 
        'business.weeklyMarketAttendance', 'business.yearsInBusiness', 
        'guarantor.business.yearsInBusiness', 'Disbursed Amount', 
        'mths_since_Dibursement Date', 'personalDetails.typeOfID_DRIVERS LICENCE', 
        'personalDetails.typeOfID_INTERNATIONAL PASSPORT', 
        'personalDetails.typeOfID_LASRAA', 'personalDetails.typeOfID_National ID', 'personalDetails.typeOfID_PVC', 
        'personalDetails.maritalStatus_Divorced', 'personalDetails.maritalStatus_Married', 'personalDetails.maritalStatus_Single',
        'guarantor.typeOfID_DRIVERS LICENCE', 'guarantor.typeOfID_INTERNATIONAL PASSPORT', 
        'guarantor.typeOfID_LASRAA', 'guarantor.typeOfID_National ID', 'guarantor.typeOfID_PVC',
        'guarantor.business.monthlyIncome_10000_50000', 'guarantor.business.monthlyIncome_50000_200000', 
        'guarantor.business.monthlyIncome_Above 200000', 
        'guarantor.business.monthlyIncome_Less than 5000_ 10000', 'guarantor.business.monthlyIncome_Less than 10_000__50_000'
        ]
    # present = x.columns.values
    missing = [i for i in expected_columns if i not in X_test.columns.values]
    X_test = X_test.reindex(columns=expected_columns)
    for i in missing:
        X_test.at[0, i] = 0
    
    X_test = X_test.fillna(0)
    X_test = X_test.astype('float32')

    return X_test


# input_dict = json.loads(raw_json.decode())       
X = X_test.copy()
data = process_event(X)

class PredictResource(object):

    def __init__(self, model):
        self.model = model

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'Hello World!'

    def on_post(self, req, resp):
        predicted_data = self.model.predict(data)

        output = {'prediction': str(predicted_data)}
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, ensure_ascii=False)

class GenerateCreditScore(object):
    def __init__(self, card):
        self.card = card

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'Hi'

    def on_post(self, req, resp):
        score = sc.scorecard_ply(X_test, self.card, only_total_score=True, print_step=0, replace_blank_na=True, var_kp = None)
        output = {'Credit score': str(score)}

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, ensure_ascii=False)
        resp.location = '/creditscore/score'
