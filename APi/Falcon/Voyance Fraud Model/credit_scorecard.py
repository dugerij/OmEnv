import scorecardpy as sc
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

dataset = pd.read_csv("/work/new ajocard.xlsx - lending-customers (2).csv")

dataset.replace(to_replace='Above ₦200,000', value='Above 200000', inplace=True)
dataset.replace(to_replace='₦50,000-₦200,000', value='50000-200000', inplace=True)
dataset.replace(to_replace='₦10,000-₦50,000', value='10000-50000', inplace=True)
dataset.replace(to_replace='₦10,000-₦50,000', value='10000-50000', inplace=True)

# 'personalDetails.typeOfID' has National ID and NATIONAL ID, which we will combine into one
dataset.replace(to_replace='NATIONAL ID', value='National ID', inplace=True)

# similarly, with 'personalDetails.maritalStatus' which has both divorced and divorce
dataset.replace(to_replace='Divorce', value='Divorced', inplace=True)

#  'personalDetails.numberOfChildren' has abnormal values, up to 9 x 10^9 and 22, we will replace all values greater than 10 with 10

dataset.loc[dataset['personalDetails.numberOfChildren'] > 10.0, 'personalDetails.numberOfChildren'] = 10.0

#  'business.type' and 'guarantor.business.type' has 582 unique entries and some are repetitions of others
dataset.loc[dataset['business.yearsInBusiness'] == 1987, 'business.yearsInBusiness'] = 35
dataset.loc[dataset['business.yearsInBusiness'] == 2000, 'business.yearsInBusiness'] = 22

# We will drop future looking columns i.e  'Repayment Start Date', 'Repayment End Date' as well as 'Loan Balance' as it will have similar implications as 'Days Outstanding' 
dataset.drop(columns=['Repayment Start Date', 'Repayment End Date', 'Loan Balance'], inplace=True)


# Change daily income from object to numbers
dataset['business.dailyIncome'] = dataset['business.dailyIncome'].replace(',', '', regex=True)
dataset['business.dailyIncome'] = pd.to_numeric(dataset['business.dailyIncome'])
dataset.loc[dataset['business.dailyIncome'] == 22, 'business.dailyIncome'] = 22000
# 
dataset['guarantor.business.monthlyIncome'] = dataset['guarantor.business.monthlyIncome'].str.replace(r'[^a-zA-Z0-9 ]', "_", regex=True) 
dataset.drop(columns=['customerId'], inplace=True)

# Drop unhelpful columns gender and religion and business.type
dataset.drop(columns=['personalDetails.gender', 'personalDetails.religion', 'business.type', 'guarantor.gender', 'guarantor.religion', 'guarantor.business.type'], inplace=True)

dataset['good_bad'] = np.where(dataset.loc[:, 'Days Outstanding'].isin([0]), 0, 1)

# We can then drop the 'Days Outstanding' column
dataset.drop(columns=['Days Outstanding'], inplace=True)
dataset['good_bad'].value_counts()

def date_columns_conv(df, column):
    today_date = (pd.to_datetime('2022-04-15', utc=True))
 
    df[column] = (pd.to_datetime(df[column], format='%Y-%m-%d'))
    df['mths_since_' + column] = round(pd.to_numeric((today_date - df[column]) / np.timedelta64(1, 'M')))
    
    df['mths_since_' + column] = df['mths_since_' + column].apply(lambda x: df['mths_since_' + column].max() if x<0 else x)
    df.drop(columns=[column], inplace=True)

date_columns_conv(dataset, 'Dibursement Date')

df_sc = sc.var_filter(dataset,y='good_bad')
X = df_sc.loc[:,df_sc.columns != 'good_bad']
y = df_sc.loc[:,df_sc.columns == 'good_bad']

train, test = sc.split_df(df_sc, 'good_bad').values()

bins = sc.woebin(df_sc, y="good_bad")

train_woe = sc.woebin_ply(train, bins)
test_woe = sc.woebin_ply(test, bins)

y_train = train_woe.loc[:,'good_bad']
X_train = train_woe.loc[:,train_woe.columns != 'good_bad']
y_test = test_woe.loc[:,'good_bad']
X_test = test_woe.loc[:,train_woe.columns != 'good_bad']

lr = LogisticRegression(penalty='l1', C=0.9, solver='saga', n_jobs=-1, random_state=21)
lr.fit(X_train, y_train)

train_pred = lr.predict_proba(X_train)[:,1]
test_pred = lr.predict_proba(X_test)[:,1]

card = sc.scorecard(bins, lr, X_train.columns, points0=100, odds0=1/25, pdo=4, basepoints_eq0=False)
train_score = sc.scorecard_ply(train, card, only_total_score=False, print_step=0, replace_blank_na=True, var_kp = None)
test_score = sc.scorecard_ply(test, card, only_total_score=False, print_step=0, replace_blank_na=True, var_kp = None)
score = sc.scorecard_ply(dataset, card, only_total_score=False, print_step=0, replace_blank_na=True, var_kp = None)

