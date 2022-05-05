#!/usr/bin/env

import json
import falcon
import numpy as np
import pandas as pd
import random
import scorecardpy as sc

random.seed(3)

def process_event(raw_json):
    input_dict = raw_json
    X_test = pd.DataFrame(input_dict, index=[0], columns=list(input_dict.keys()))
    
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

def process_card_data(raw_json):
    input_dict = raw_json
    X_test = pd.DataFrame(input_dict, index=[0], columns=list(input_dict.keys()))
    
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

    return X_test

class PredictResource(object):
    def __init__(self, model):
        self.model = model

    def on_post(self, req, resp):
        data = req.get_media()
        data = process_event(raw_json=data)

        predicted_data = self.model.predict(data)
        output = {'prediction': str(predicted_data)}

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output, ensure_ascii=False)

class GenerateCreditScore(object):
    def __init__(self, card):
        self.card = card

    def on_post(self, req, resp):
        data = req.get_media()
        data = process_card_data(data)

        score = sc.scorecard_ply(data, self.card, only_total_score=True, print_step=0, replace_blank_na=True, var_kp = None)
        output = {'Credit score': (str(score))[-5:]}

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output, ensure_ascii=False)