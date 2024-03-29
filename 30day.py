import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

df = pd.read_csv('../input/30days-folds/train_folds.csv')
df_test = pd.read_csv('../input/30-days-of-ml/test.csv')
sample_submission = pd.read_csv('../input/30-days-of-ml/sample_submission.csv')

xgb_params = {
    'random_state': 1, 
    # gpu
#     'tree_method': 'gpu_hist', 
#     'gpu_id': 0, 
#     'predictor': 'gpu_predictor',
    # cpu
    'n_jobs': 4,
    'booster': 'gbtree',
    'n_estimators': 10000,
    # optimized params
    'learning_rate': 0.03628302216953097,
    'reg_lambda': 0.0008746338866473539,
    'reg_alpha': 23.13181079976304,
    'subsample': 0.7875490025178415,
    'colsample_bytree': 0.11807135201147481,
    'max_depth': 3
}

final_predictions = []
scores = []
for fold in range(5):
    xtrain = df[df.kfold != fold].reset_index(drop=True)
    xvalid = df[df.kfold == fold].reset_index(drop=True)
    xtest = df_test.copy()
    
    ytrain = xtrain.target
    yvalid = xvalid.target
    
    xtrain = xtrain[useful_features]
    xvalid = xvalid[useful_features]
    
    ordinal_encoder = preprocessing.OrdinalEncoder()
    xtrain[object_cols] = ordinal_encoder.fit_transform(xtrain[object_cols])
    xvalid[object_cols] = ordinal_encoder.transform(xvalid[object_cols])
    xtest[object_cols] = ordinal_encoder.transform(xtest[object_cols])
    
    model= XGBRegressor(**xgb_params)
    model.fit(
        xtrain, ytrain,
        early_stopping_rounds=300,
        eval_set=[(xvalid, yvalid)], 
        verbose=1000
    )
    preds_valid = model.predict(xvalid)
    test_preds = model.predict(xtest)
    final_predictions.append(test_preds)
    rmse = mean_squared_error(yvalid, preds_valid, squared=False)
    scores.append(rmse)
    print(fold, rmse)

print(np.mean(scores), np.std(scores))

preds = np.mean(np.column_stack(final_predictions), axis=1)
sample_submission.target = preds
sample_submission.to_csv("submission.csv", index=False)
