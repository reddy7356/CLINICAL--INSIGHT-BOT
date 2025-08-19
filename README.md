# Clinical Insight Bot for Anesthesiology

A specialized tool for extracting anesthesia-relevant clinical information from Electronic Medical Record (EMR) text. This bot processes patient chart text and outputs structured JSON containing key information needed for pre-operative, intra-operative, and post-operative anesthesia planning.

## Features

### Comprehensive Data Extraction
- **Patient Demographics**: Age, weight, height, gender
- **ASA Physical Status**: Automated ASA classification detection
- **Allergies**: Drug allergies and NKDA status
- **Medications**: Focus on anesthesia-relevant drugs (anticoagulants, insulin, cardiac meds)
- **Comorbidities**: Cardiac, pulmonary, renal, hepatic, neurologic, endocrine conditions
- **Airway Assessment**: Mallampati score, mouth opening, predicted difficulty
- **Laboratory Values**: Hemoglobin, platelets, INR/PT/PTT, creatinine, glucose
- **Surgical Plan**: Procedure, position, duration, approach
- **Risk Assessment**: Aspiration, cardiac, bleeding, and airway risks

### Smart Pattern Recognition
- Uses regex patterns to identify clinical values and measurements
- Keyword-based detection for conditions and medications
- Handles common medical abbreviations and terminology
- Outputs "Not Found" for missing information to ensure completeness

## Usage

### Command Line Interface

#### Basic Usage
```bash
python clinical_insight_bot.py "PATIENT EMR TEXT HERE"
```

#### File Input
```bash
python clinical_insight_bot.py --file patient_chart.txt
```

### Python API

```python
from clinical_insight_bot import ClinicalInsightBot

# Initialize the bot
bot = ClinicalInsightBot()

# Process EMR text
emr_text = """
65-year-old male, weight 80kg, height 175cm
ASA III, allergies: NKDA
History of hypertension, diabetes mellitus
Taking metoprolol, insulin, aspirin
Scheduled for laparoscopic cholecystectomy
Supine position, estimated 2 hours
Hemoglobin 12.5, Creatinine 1.2
"""

results = bot.process_emr_text(emr_text)
print(json.dumps(results, indent=2))
```

## Output Format

The bot outputs structured JSON with the following sections:

```json
{
  "patient_info": {
    "age": "65 years",
    "weight": "80kg",
    "height": "175cm", 
    "gender": "Male"
  },
  "pre_operative": {
    "asa_status": "ASA III",
    "allergies": "NKDA (No Known Drug Allergies)",
    "medications": {
      "anticoagulants": "Aspirin",
      "insulin": "Insulin",
      "cardiac_meds": "Metoprolol",
      "other_relevant": "Not Found"
    },
    "comorbidities": {
      "cardiac": "hypertension",
      "pulmonary": "Not Found",
      "renal": "Not Found",
      "hepatic": "Not Found",
      "neurologic": "Not Found",
      "endocrine": "diabetes, insulin"
    },
    "airway_assessment": {
      "mallampati": "Not Found",
      "mouth_opening": "Not Found",
      "neck_mobility": "Not Found",
      "thyromental_distance": "Not Found",
      "dentition": "Not Found",
      "predicted_difficulty": "Not Found"
    },
    "laboratory_values": {
      "hemoglobin": "12.5 g/dL",
      "platelet_count": "Not Found",
      "inr_pt_ptt": "Not Found",
      "creatinine": "1.2 mg/dL",
      "glucose": "Not Found",
      "electrolytes": "Not Found"
    },
    "device_implants": "Not Found",
    "npo_status": "Not Found"
  },
  "surgical_plan": {
    "procedure": "Laparoscopic Cholecystectomy",
    "surgical_position": "Supine",
    "estimated_duration": "2 hours",
    "surgeon": "Not Found",
    "approach": "Not Found"
  },
  "intra_operative": {
    "special_monitoring": "Not Found",
    "vascular_access": "Not Found", 
    "blood_products": "Not Found",
    "regional_anesthesia": "Not Found",
    "temperature_management": "Not Found",
    "fluid_management": "Not Found"
  },
  "post_operative": {
    "planned_disposition": "Not Found",
    "pain_management": "Not Found",
    "icu_monitoring": "Not Found",
    "ventilator_weaning": "Not Found"
  },
  "risk_assessment": {
    "aspiration_risk": "Not Found",
    "difficult_airway": "Not Found", 
    "cardiac_risk": "Moderate",
    "bleeding_risk": "Elevated"
  },
  "metadata": {
    "processed_timestamp": "2024-01-15T10:30:00.000000",
    "version": "1.0",
    "extraction_confidence": "Automated extraction - verify critical values"
  }
}
```

## Clinical Categories Detected

### Medications
- **Anticoagulants**: Warfarin, Heparin, Rivaroxaban, Apixaban, Dabigatran, Aspirin, Clopidogrel
- **Diabetes**: Insulin, Metformin, Glipizide, Glyburide  
- **Cardiac**: Beta-blockers, ACE inhibitors, Calcium channel blockers

### Conditions
- **Cardiac**: Hypertension, CAD, MI, CHF, Arrhythmias, Valve disease
- **Pulmonary**: COPD, Asthma, Sleep apnea, Pulmonary embolism
- **Renal**: CKD, Renal failure, Dialysis
- **Endocrine**: Diabetes mellitus, thyroid disorders

### Risk Factors
- **Aspiration**: NPO status, GERD, gastroparesis, recent meals
- **Cardiac**: Recent MI, unstable angina, severe AS, decompensated CHF
- **Bleeding**: Anticoagulant use, bleeding disorders, thrombocytopenia
- **Airway**: Difficult airway predictors, Mallampati score

## Installation

### Requirements
- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

### Setup
1. Clone or download the repository
2. Ensure Python 3.7+ is installed
3. Run directly - no pip install required

```bash
# Make executable (optional)
chmod +x clinical_insight_bot.py

# Run with Python
python clinical_insight_bot.py --help
```

## Important Notes

### Clinical Use Disclaimer
⚠️ **IMPORTANT**: This tool is for educational and informational purposes only. It is NOT intended for clinical decision-making without proper medical oversight. Always verify extracted information against the original medical records and clinical judgment.

### Accuracy Considerations
- The bot uses pattern matching and keyword detection
- Medical abbreviations and terminology may vary between institutions
- Complex medical history may require manual review
- Always verify critical values before clinical use

### Data Privacy
- The tool processes text locally - no data is sent to external servers
- Ensure compliance with HIPAA and institutional policies
- Consider de-identification of patient data before processing

## Customization

### Adding New Patterns
You can extend the bot's capabilities by modifying the `patterns` and `keywords` dictionaries in the `ClinicalInsightBot` class:

```python
# Add new medication categories
self.keywords['beta_blockers'] = ['metoprolol', 'atenolol', 'propranolol']

# Add new regex patterns
self.patterns['bmi'] = [r'BMI:?\s*(\d+\.?\d*)']
```

### Custom Risk Assessment
Extend the `assess_risks()` method to include institution-specific risk factors:

```python
def assess_risks(self, text: str) -> None:
    # Add custom risk assessment logic
    if 'morbid obesity' in text.lower():
        self.insight.data['risk_assessment']['airway_risk'] = "High - obesity"
```

## Example Use Cases

### Pre-operative Assessment
- Quickly extract ASA status and comorbidities for anesthesia planning
- Identify medication interactions and timing considerations
- Assess airway difficulty and plan appropriate equipment

### Intra-operative Planning  
- Review planned surgical position and duration
- Identify needs for special monitoring or vascular access
- Plan for blood product availability

### Post-operative Care
- Determine appropriate recovery location (PACU vs ICU)
- Plan pain management strategy
- Assess ventilator weaning potential

## EPIC Demo (Sandbox)

Run a complete demo of the Clinical Insight Bot using a synthetic EPIC patient (no OAuth, no network calls):

```bash
pip install -r requirements_epic.txt
python epic_demo_patient.py
```

This will print anesthesia-focused insights and save them to a timestamped JSON file like `epic_demo_patient_insights_YYYYMMDD_HHMMSS.json`.

## Support

For questions, issues, or feature requests, please refer to the documentation or contact the development team.

## License

This project is intended for educational and research purposes. Please ensure compliance with all applicable medical device regulations and institutional policies before clinical use. # CLINICAL--INSIGHT-BOT
