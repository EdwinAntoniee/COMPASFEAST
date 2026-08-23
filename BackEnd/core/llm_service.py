"""Ollama service for repair guidance and chat."""

from __future__ import annotations

import json
import re
from typing import Any

import ollama

OLLAMA_MODEL = "qwen-model"

SYSTEM_INSTRUCTION = (
    "You are a senior field technician assistant for conveyor and "
    "electrical motor machinery. Give practical, concise, safe guidance."
)

def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|\s*```$", "", cleaned, flags=re.IGNORECASE).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("LLM response did not contain a JSON object") from None
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("LLM response JSON must be an object")
    return value


def _normalize_guidance(value: dict[str, Any]) -> dict[str, Any]:
    required = (
        "summary",
        "root_cause",
        "recommended_actions",
        "safety_notes",
        "estimated_downtime_minutes",
    )
    missing = [key for key in required if key not in value]
    if missing:
        raise ValueError(f"LLM response missing keys: {', '.join(missing)}")

    actions = value["recommended_actions"]
    safety_notes = value["safety_notes"]
    if not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
        raise ValueError("recommended_actions must be a list of strings")
    if not isinstance(safety_notes, list) or not all(isinstance(item, str) for item in safety_notes):
        raise ValueError("safety_notes must be a list of strings")

    downtime = value["estimated_downtime_minutes"]
    if isinstance(downtime, bool) or not isinstance(downtime, int):
        raise ValueError("estimated_downtime_minutes must be an integer")

    return {
        "summary": str(value["summary"]),
        "root_cause": str(value["root_cause"]),
        "recommended_actions": actions,
        "safety_notes": safety_notes,
        "estimated_downtime_minutes": downtime,
    }


def _normalize_repair_steps(value: dict[str, Any]) -> list[str]:
    actions = value.get("recommended_actions")
    if not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
        raise ValueError("recommended_actions must be a list of strings")
    return actions


def generate_repair_guidance(
    machine_id: str,
    failure_mode: str,
    failure_mode_label: str,
    sensor_data: dict[str, Any],
) -> list[str]:
    """Ask Ollama only for repair steps."""
    fallback = ["Inspect the machine manually and follow site procedures."]

    try:
        prompt = (
            "Act as an expert factory mechanic and analyze this machine failure.\n"
            f"Machine ID: {machine_id}\n"
            f"Failure mode: {failure_mode} ({failure_mode_label})\n"
            f"Sensor data: {json.dumps(sensor_data, default=str)}\n\n"
            "Output strictly valid JSON as an object with exactly one key: "
            "recommended_actions, whose value is a list of strings."
        )
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt},
            ],
        )
        response_text = response["message"]["content"]
        return _normalize_repair_steps(_extract_json(response_text))
    except Exception:
        return fallback


def chat_with_bot(chat_history: list[dict[str, str]]) -> str:
    """Generate a plain-text reply for a list of chat messages."""
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=chat_history)
        return response["message"]["content"].strip()
    except Exception:
        return "Sorry, I could not connect to the local AI service."
