import numpy as np
import pandas as pd

def preprocess_cleaning(df_in):
    """Clean raw dataset: drop UDI and Product ID if present, encode machine Type."""
    X_c = df_in.copy()
    drop_cols = [c for c in ['udi', 'product_id'] if c in X_c.columns]
    if drop_cols:
        X_c = X_c.drop(columns=drop_cols)
    type_map = {'L': 0, 'M': 1, 'H': 2}
    if 'type' in X_c.columns:
        X_c['type'] = X_c['type'].map(type_map).fillna(X_c['type'])
    return X_c

def feature_engineering(df_in):
    """Engineers physics-based features (log_rotational_speed, temp_diff, power_w, tool_wear_torque)."""
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

FAILURE_LABELS = ['TWF (Tool Wear Failure)', 'HDF (Heat Dissipation Failure)', 'PWF (Power Failure)', 'OSF (Overstrain Failure)', 'RNF (Random Failure)']

def interpret_prediction(pred_binary_array):
    """Translates 5-column binary output array into human-readable failure mode names."""
    row = pred_binary_array[0] if len(pred_binary_array.shape) > 1 else pred_binary_array
    active = [FAILURE_LABELS[i] for i, val in enumerate(row) if val == 1]
    if not active:
        return "Normal (No Failure Detected)"
    return " + ".join(active)
