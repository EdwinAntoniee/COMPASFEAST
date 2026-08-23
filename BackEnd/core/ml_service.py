import os
import joblib
import numpy as np
import pandas as pd


from src.pipeline_utils import preprocess_cleaning, feature_engineering, PerTargetScaleWeightedClassifier

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
MODEL_PATHS = (
    os.path.join(MODEL_DIR, "smart_maintenance_pipeline.pkl"),
)

FAILURE_MODES = ("twf", "hdf", "pwf", "osf", "rnf")
FAILURE_MODE_LABELS = {
    "twf": "Tool Wear Failure",
    "hdf": "Heat Dissipation Failure",
    "pwf": "Power Failure",
    "osf": "Overstrain Failure",
    "rnf": "Random Failure",
}

RISK_BY_CONFIDENCE = [
    (0.9, "Critical"),
    (0.75, "High"),
    (0.5, "Medium"),
]

def _load_pipeline():
    for model_path in MODEL_PATHS:
        if os.path.exists(model_path):
            return joblib.load(model_path) # Sekarang load akan berhasil 100%
    raise FileNotFoundError("Model .pkl tidak ditemukan di folder models!")

def _risk_level_for(confidence: float) -> str:
    for threshold, level in RISK_BY_CONFIDENCE:
        if confidence >= threshold:
            return level
    return "Low"


def _failure_details(mode: str, sensor_data: dict) -> tuple[str, str]:
    details = {
        "twf": (
            "Tool wear failure detected.",
            f"Tool wear is {sensor_data['tool_wear_min']:.1f} minutes, increasing wear and failure risk.",
        ),
        "hdf": (
            "Heat dissipation failure detected.",
            f"The process-to-air temperature difference is {sensor_data['process_temperature_k'] - sensor_data['air_temperature_k']:.1f} K, indicating insufficient heat dissipation.",
        ),
        "pwf": (
            "Power failure detected.",
            f"The machine is operating at {sensor_data['rotational_speed_rpm']:.1f} RPM and {sensor_data['torque_nm']:.1f} Nm, indicating an abnormal power load.",
        ),
        "osf": (
            "Overstrain failure detected.",
            f"Torque is {sensor_data['torque_nm']:.1f} Nm with {sensor_data['tool_wear_min']:.1f} minutes of tool wear, creating excessive mechanical strain.",
        ),
        "rnf": (
            "Random failure detected.",
            "The model detected an anomaly that does not clearly match the main sensor-based failure patterns.",
        ),
    }
    return details[mode]


def repair_case(mode: str, sensor_data: dict) -> dict:
    cases = {
        "twf": ("Excessive tool wear is increasing mechanical friction and failure risk.", "Stop the machine and isolate power before replacing the tool.", 30),
        "hdf": ("The machine is not dissipating process heat effectively.", "Allow hot components to cool before inspection.", 45),
        "pwf": ("The speed and torque combination indicates an abnormal power load.", "Disconnect and lock out electrical power before testing.", 60),
        "osf": ("High torque combined with tool wear is creating excessive mechanical strain.", "Keep clear of moving parts and isolate the drive before inspection.", 50),
        "rnf": ("The sensor pattern indicates an anomaly that does not match a known failure category.", "Use normal lockout and verification procedures before troubleshooting.", 40),
    }
    root_cause, safety_note, downtime = cases[mode]
    return {
        "root_cause": root_cause,
        "safety_notes": [safety_note],
        "estimated_downtime_minutes": downtime,
    }

def predict_condition(sensor_data: dict) -> dict:
    pipeline = _load_pipeline()

    x_raw = pd.DataFrame([{
        "type": sensor_data["machine_type"],
        "air_temperature_k": sensor_data["air_temperature_k"],
        "process_temperature_k": sensor_data["process_temperature_k"],
        "rotational_speed_rpm": sensor_data["rotational_speed_rpm"],
        "torque_nm": sensor_data["torque_nm"],
        "tool_wear_min": sensor_data["tool_wear_min"],
    }])

    prediction = np.asarray(pipeline.predict(x_raw))
    probabilities = pipeline.predict_proba(x_raw)
    
    mode_predictions = prediction[0].astype(bool)
    raw_confidences = np.array([
        float(prob[0, 1]) if prob.shape[1] > 1 else float(prob[0, 0])
        for prob in probabilities[:len(FAILURE_MODES)]
    ])
    mode_confidences = raw_confidences
    
    failed_modes = [
        mode for mode, is_failed in zip(FAILURE_MODES, mode_predictions) if is_failed
    ]
    
    if not failed_modes:
        return {
            "status": "Normal",
            "failure_mode": None,
            "failure_mode_label": None,
            "confidence": round(float(1 - raw_confidences.max()), 4),
            "risk_level": "Low",
            "summary": "No actionable failure mode was detected.",
            "root_cause": "The sensor readings do not currently indicate a known failure pattern.",
            "additional_diagnoses": [],
        }

    primary_mode = max(
        failed_modes,
        key=lambda mode: mode_confidences[FAILURE_MODES.index(mode)],
    )
    candidate_modes = sorted(
        FAILURE_MODES,
        key=lambda mode: mode_confidences[FAILURE_MODES.index(mode)],
        reverse=True,
    )[:3]
    failed_confidence = float(mode_confidences[FAILURE_MODES.index(primary_mode)])
    summary, root_cause = _failure_details(primary_mode, sensor_data)

    additional_diagnoses = []
    for mode in candidate_modes:
        if mode == primary_mode:
            continue
        confidence = float(mode_confidences[FAILURE_MODES.index(mode)])
        additional_diagnoses.append({
            "status": "Failed" if mode in failed_modes else "Possible",
            "failure_mode": mode.upper(),
            "failure_mode_label": FAILURE_MODE_LABELS[mode],
            "confidence": round(confidence, 4),
            "risk_level": _risk_level_for(confidence),
        })
    
    return {
        "status": "Failed",
        "failure_mode": primary_mode.upper(),
        "failure_mode_label": FAILURE_MODE_LABELS[primary_mode],
        "confidence": round(failed_confidence, 4),
        "risk_level": _risk_level_for(failed_confidence),
        "summary": summary,
        "root_cause": root_cause,
        "additional_diagnoses": additional_diagnoses,
    }