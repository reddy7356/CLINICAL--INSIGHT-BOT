#!/usr/bin/env python3
"""
EPIC Demo Patient Application for Clinical Insight Bot

Runs a complete, non-interactive demo using synthetic EPIC FHIR data
to generate anesthesia-focused clinical insights. No real OAuth or
network calls are performed. This is safe to run locally.
"""

import json
from datetime import datetime

from epic_integration import EpicFHIRClient


def build_demo_patient_fhir_bundle() -> dict:
    """Return a synthetic EPIC-like FHIR data bundle for demo use."""
    return {
        "patient": {
            "id": "epic-demo-patient-001",
            "name": [{"given": ["Jane"], "family": "Doe"}],
            "birthDate": "1980-07-15",
            "gender": "female",
        },
        "conditions": [
            {
                "code": {
                    "text": "Type 2 Diabetes Mellitus",
                    "coding": [{"display": "Type 2 Diabetes Mellitus"}],
                }
            },
            {
                "code": {
                    "text": "Hypertension",
                    "coding": [{"display": "Essential Hypertension"}],
                }
            },
        ],
        "medications": [
            {
                "medicationCodeableConcept": {
                    "text": "Metformin 500mg",
                    "coding": [{"display": "Metformin 500mg tablets"}],
                },
                "dosageInstruction": [{"text": "Take twice daily with meals"}],
            },
            {
                "medicationCodeableConcept": {
                    "text": "Lisinopril 10mg",
                    "coding": [{"display": "Lisinopril 10mg tablets"}],
                },
                "dosageInstruction": [{"text": "Take once daily"}],
            },
            {
                "medicationCodeableConcept": {
                    "text": "Aspirin 81mg",
                    "coding": [{"display": "Aspirin 81mg chewable"}],
                },
                "dosageInstruction": [{"text": "Take once daily"}],
            },
        ],
        "allergies": [
            {
                "code": {
                    "text": "Penicillin",
                    "coding": [{"display": "Penicillin allergy"}],
                },
                "reaction": [
                    {"manifestation": [{"text": "Rash, difficulty breathing"}]}
                ],
            }
        ],
        "observations": [
            {
                "code": {
                    "text": "Hemoglobin A1c",
                    "coding": [{"display": "Hemoglobin A1c"}],
                },
                "valueQuantity": {"value": 7.2, "unit": "%"},
            },
            {
                "code": {
                    "text": "Hemoglobin",
                    "coding": [{"display": "Hemoglobin"}],
                },
                "valueQuantity": {"value": 11.8, "unit": "g/dL"},
            },
            {
                "code": {
                    "text": "Creatinine",
                    "coding": [{"display": "Creatinine"}],
                },
                "valueQuantity": {"value": 1.3, "unit": "mg/dL"},
            },
            {
                "code": {
                    "text": "Blood Pressure",
                    "coding": [{"display": "Blood Pressure"}],
                },
                "valueString": "138/86 mmHg",
            },
        ],
        "procedures": [
            {
                "code": {
                    "text": "Appendectomy",
                    "coding": [{"display": "Laparoscopic appendectomy"}],
                },
                "performedDateTime": "2019-05-15",
            }
        ],
    }


def run_demo() -> dict:
    """Run the EPIC demo: convert FHIR data to text, analyze, return insights."""
    # No real network or OAuth is used. The client is only used for conversion utilities
    # and to access the integrated Clinical Insight Bot instance.
    client = EpicFHIRClient(client_id="demo", fhir_base_url="demo")

    demo_patient_data = build_demo_patient_fhir_bundle()

    # Convert to free text that the Clinical Insight Bot expects
    patient_text = client.convert_fhir_to_text(demo_patient_data)

    # Generate insights
    insights = client.insight_bot.process_emr_text(patient_text)

    # Attach demo metadata
    insights.setdefault("metadata", {})
    insights["metadata"].update(
        {
            "fhir_source": {
                "fhir_base_url": "demo",
                "patient_id": demo_patient_data["patient"]["id"],
                "data_extraction_timestamp": datetime.now().isoformat(),
                "epic_version": "FHIR R4 (demo)",
            }
        }
    )

    return insights


def main() -> None:
    print("=== EPIC Demo Patient: Clinical Insight Bot ===\n")
    print("Running with synthetic FHIR data (no network, no OAuth) ...\n")

    insights = run_demo()

    # Pretty print
    print("Clinical Insights:\n" + "-" * 40)
    print(json.dumps(insights, indent=2))

    # Save to a timestamped JSON file
    filename = f"epic_demo_patient_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as output_file:
        json.dump(insights, output_file, indent=2)
    print(f"\nSaved insights to: {filename}")


if __name__ == "__main__":
    main()


