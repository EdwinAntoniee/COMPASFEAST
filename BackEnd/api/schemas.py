from typing import Literal

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    machine_type: Literal["L", "M", "H"] = Field(
        ..., description="AI4I product type: L (Low), M (Medium), or H (High)"
    )
    air_temperature_k: float = Field(..., description="Ambient air temperature near the machine (Kelvin)")
    process_temperature_k: float = Field(..., description="Process/internal machine temperature (Kelvin)")
    rotational_speed_rpm: float = Field(..., description="Motor rotational speed (RPM)")
    torque_nm: float = Field(..., description="Torque (Newton-meter)")
    tool_wear_min: float = Field(..., description="Tool usage time (minutes)")


class PredictRequest(BaseModel):
    machine_id: str = Field(..., examples=["M14860"])
    sensor_data: SensorData


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)


class Diagnosis(BaseModel):
    status: str            # "Normal" | "Failed"
    failure_mode: str | None = None   # "TWF" | "HDF" | "PWF" | "OSF" | "RNF" | None
    failure_mode_label: str | None = None
    confidence: float      # 0.0 - 1.0
    risk_level: str        # "Low" | "Medium" | "High" | "Critical"


class AdditionalDiagnosis(Diagnosis):
    pass


class RepairGuidance(BaseModel):
    summary: str
    root_cause: str
    recommended_actions: list[str]
    safety_notes: list[str]
    estimated_downtime_minutes: int | None = None


class PredictResponse(BaseModel):
    machine_id: str
    diagnosis: Diagnosis
    additional_diagnoses: list[AdditionalDiagnosis] = Field(default_factory=list)
    repair_guidance: RepairGuidance | None = None
    generated_by: str      # "predictive_ai" | "predictive_ai+generative_ai"
