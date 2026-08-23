import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from lightgbm import LGBMClassifier

def preprocess_cleaning(df_in):
    X_c = df_in.copy()
    drop_cols = [c for c in ['udi', 'product_id'] if c in X_c.columns]
    if drop_cols:
        X_c = X_c.drop(columns=drop_cols)
    type_map = {'L': 0, 'M': 1, 'H': 2}
    if 'type' in X_c.columns:
        X_c['type'] = X_c['type'].map(type_map).fillna(X_c['type'])
    return X_c

def feature_engineering(df_in):
    X_fe = df_in.copy()
    if 'rotational_speed_rpm' in X_fe.columns:
        X_fe['log_rotational_speed'] = np.log1p(X_fe['rotational_speed_rpm'])
        rpm = X_fe['rotational_speed_rpm']
    else:
        rpm = np.expm1(X_fe['log_rotational_speed'])
        
    X_fe['temp_diff'] = X_fe['process_temperature_k'] - X_fe['air_temperature_k']
    X_fe['power_w'] = X_fe['torque_nm'] * (rpm * 2 * np.pi / 60)
    X_fe['tool_wear_torque'] = X_fe['tool_wear_min'] * X_fe['torque_nm']
    
    if 'rotational_speed_rpm' in X_fe.columns:
        X_fe = X_fe.drop(columns=['rotational_speed_rpm'])
        
    return X_fe

class PerTargetScaleWeightedClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, n_estimators=150, learning_rate=0.05, max_depth=6, random_state=42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.models_ = {}
        self.columns_ = []
        self.thresholds_ = {}

    def fit(self, X, y):
        self.columns_ = list(y.columns) if isinstance(y, pd.DataFrame) else [f'col_{i}' for i in range(y.shape[1])]
        y_df = pd.DataFrame(y, columns=self.columns_) if not isinstance(y, pd.DataFrame) else y
        
        for col in self.columns_:
            pos_cnt = (y_df[col] == 1).sum()
            neg_cnt = (y_df[col] == 0).sum()
            w = neg_cnt / max(1, pos_cnt)
            
            if col == 'twf':
                clf = LGBMClassifier(n_estimators=200, learning_rate=0.03, max_depth=6, scale_pos_weight=w*0.8, random_state=self.random_state, verbose=-1)
                thresh = 0.3
            elif col == 'rnf':
                clf = LGBMClassifier(n_estimators=100, learning_rate=0.05, max_depth=4, scale_pos_weight=w*0.5, random_state=self.random_state, verbose=-1)
                thresh = 0.2
            else:
                clf = LGBMClassifier(n_estimators=self.n_estimators, learning_rate=self.learning_rate, max_depth=self.max_depth, scale_pos_weight=w, random_state=self.random_state, verbose=-1)
                thresh = 0.5
                
            clf.fit(X, y_df[col])
            self.models_[col] = clf
            self.thresholds_[col] = thresh
        return self

    def predict(self, X):
        preds = {}
        for col in self.columns_:
            probas = self.models_[col].predict_proba(X)[:, 1]
            thresh = self.thresholds_[col]
            preds[col] = (probas >= thresh).astype(int)
        return pd.DataFrame(preds)[self.columns_].values

    def predict_proba(self, X):
        return [self.models_[col].predict_proba(X) for col in self.columns_]

FAILURE_LABELS = ['TWF (Tool Wear Failure)', 'HDF (Heat Dissipation Failure)', 'PWF (Power Failure)', 'OSF (Overstrain Failure)', 'RNF (Random Failure)']

def interpret_prediction(pred_binary_array):
    row = pred_binary_array[0] if len(pred_binary_array.shape) > 1 else pred_binary_array
    active = [FAILURE_LABELS[i] for i, val in enumerate(row) if val == 1]
    if not active:
        return "Normal (No Failure Detected)"
    return " + ".join(active)
