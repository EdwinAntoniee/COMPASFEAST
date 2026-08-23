from fastapi import APIRouter, HTTPException

from api.schemas import (
    AdditionalDiagnosis,
    ChatRequest,
    Diagnosis,
    PredictRequest,
    PredictResponse,
    RepairGuidance,
)
from core import llm_service
from core import ml_service

router = APIRouter(prefix="/api/v1", tags=["predictive-maintenance"])


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        reply = llm_service.chat_with_bot(
            [message.model_dump() for message in request.messages]
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"LLM service error: {exc}") from exc
    return {"reply": reply}


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    machine_id = request.machine_id
    sensor_data = request.sensor_data.model_dump()

    # 2. Jalankan Predictive AI
    try:
        prediction = ml_service.predict_condition(sensor_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model .pkl not available.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Predictive AI error: {e}")

    diagnosis = Diagnosis(
        status=prediction["status"],
        failure_mode=prediction["failure_mode"],
        failure_mode_label=prediction["failure_mode_label"],
        confidence=prediction["confidence"],
        risk_level=prediction["risk_level"],
    )

    additional_diagnoses = [
        AdditionalDiagnosis(**item) for item in prediction["additional_diagnoses"]
    ]
    repair_guidance = None
    generated_by = "predictive_ai"
    if prediction["status"] == "Failed":
        case = ml_service.repair_case(prediction["failure_mode"].lower(), sensor_data)
        repair_guidance = RepairGuidance(
            summary=prediction["summary"],
            root_cause=case["root_cause"],
            safety_notes=case["safety_notes"],
            estimated_downtime_minutes=case["estimated_downtime_minutes"],
            recommended_actions=llm_service.generate_repair_guidance(
                machine_id=machine_id,
                failure_mode=prediction["failure_mode"],
                failure_mode_label=prediction["failure_mode_label"],
                sensor_data=sensor_data,
            ),
        )
        generated_by = "predictive_ai+generative_ai"

    return PredictResponse(
        machine_id=machine_id,
        diagnosis=diagnosis,
        additional_diagnoses=additional_diagnoses,
        repair_guidance=repair_guidance,
        generated_by=generated_by,
    )
