#!/usr/bin/env python3
"""
Clinical Insight Bot for Anesthesiology
Extracts key anesthesia-relevant information from EMR text and outputs structured JSON.
"""

import json
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClinicalInsight:
    """Data structure for clinical insights relevant to anesthesia"""
    
    def __init__(self):
        self.data = {
            "patient_info": {
                "age": "Not Found",
                "weight": "Not Found",
                "height": "Not Found",
                "gender": "Not Found"
            },
            "pre_operative": {
                "asa_status": "Not Found",
                "allergies": "Not Found",
                "medications": {
                    "anticoagulants": "Not Found",
                    "insulin": "Not Found",
                    "cardiac_meds": "Not Found",
                    "other_relevant": "Not Found"
                },
                "comorbidities": {
                    "cardiac": "Not Found",
                    "pulmonary": "Not Found",
                    "renal": "Not Found",
                    "hepatic": "Not Found",
                    "neurologic": "Not Found",
                    "endocrine": "Not Found"
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
                    "hemoglobin": "Not Found",
                    "platelet_count": "Not Found",
                    "inr_pt_ptt": "Not Found",
                    "creatinine": "Not Found",
                    "glucose": "Not Found",
                    "electrolytes": "Not Found"
                },
                "device_implants": "Not Found",
                "npo_status": "Not Found"
            },
            "surgical_plan": {
                "procedure": "Not Found",
                "surgical_position": "Not Found",
                "estimated_duration": "Not Found",
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
                "cardiac_risk": "Not Found",
                "bleeding_risk": "Not Found"
            }
        }


class ClinicalInsightBot:
    """Main bot class for extracting clinical insights from EMR text"""
    
    def __init__(self):
        self.insight = ClinicalInsight()
        
        # Define regex patterns for common clinical findings
        self.patterns = {
            'age': [
                r'(\d+)[-\s]?(?:year|yr|yo)\s?(?:old)?',
                r'age:?\s*(\d+)',
                r'(\d+)\s?y\.?o\.?'
            ],
            'weight': [
                r'weight:?\s*(\d+\.?\d*)\s*(?:kg|pounds?|lbs?)',
                r'(\d+\.?\d*)\s*(?:kg|pounds?|lbs?)'
            ],
            'height': [
                r'height:?\s*(\d+\.?\d*)\s*(?:cm|inches?|in|ft)',
                r'(\d+\.?\d*)\s*(?:cm|inches?|in)'
            ],
            'gender': [
                r'(?:gender|sex):?\s*(male|female|m|f)',
                r'\b(male|female)\b'
            ],
            'asa': [
                r'ASA\s*(?:status|class|classification)?:?\s*([I1-6V]+)',
                r'ASA\s*([I1-6V]+)',
                r'American Society.*?([I1-6V]+)'
            ],
            'allergies': [
                r'(?:allergies?|NKDA|NKA):?\s*([^.\n]+)',
                r'allergic to:?\s*([^.\n]+)',
                r'allergy:?\s*([^.\n]+)'
            ],
            'medications': [
                r'(?:medications?|meds?|home medications?):?\s*([^.\n]+)',
                r'taking:?\s*([^.\n]+)',
                r'prescribed:?\s*([^.\n]+)'
            ]
        }
        
        # Keywords for different categories
        self.keywords = {
            'anticoagulants': ['warfarin', 'coumadin', 'heparin', 'rivaroxaban', 'xarelto', 'apixaban', 'eliquis', 'dabigatran', 'pradaxa', 'aspirin', 'plavix', 'clopidogrel'],
            'cardiac_conditions': ['hypertension', 'CAD', 'coronary artery disease', 'MI', 'myocardial infarction', 'CHF', 'heart failure', 'arrhythmia', 'atrial fibrillation', 'valve disease'],
            'pulmonary_conditions': ['COPD', 'asthma', 'sleep apnea', 'OSA', 'pulmonary embolism', 'pneumonia', 'lung disease'],
            'renal_conditions': ['chronic kidney disease', 'CKD', 'renal failure', 'dialysis', 'kidney disease'],
            'diabetes': ['diabetes', 'DM', 'insulin', 'metformin', 'diabetic'],
            'surgical_positions': ['supine', 'prone', 'lateral', 'lithotomy', 'trendelenburg', 'reverse trendelenburg', 'sitting', 'beach chair']
        }
    
    def extract_patient_info(self, text: str) -> None:
        """Extract basic patient demographics"""
        text_lower = text.lower()
        
        # Age extraction
        for pattern in self.patterns['age']:
            match = re.search(pattern, text_lower)
            if match:
                self.insight.data['patient_info']['age'] = f"{match.group(1)} years"
                break
        
        # Weight extraction
        for pattern in self.patterns['weight']:
            match = re.search(pattern, text_lower)
            if match:
                self.insight.data['patient_info']['weight'] = match.group(0)
                break
        
        # Height extraction
        for pattern in self.patterns['height']:
            match = re.search(pattern, text_lower)
            if match:
                self.insight.data['patient_info']['height'] = match.group(0)
                break
        
        # Gender extraction
        for pattern in self.patterns['gender']:
            match = re.search(pattern, text_lower)
            if match:
                gender = match.group(1).lower()
                self.insight.data['patient_info']['gender'] = "Male" if gender in ['male', 'm'] else "Female"
                break
    
    def extract_asa_status(self, text: str) -> None:
        """Extract ASA physical status classification"""
        for pattern in self.patterns['asa']:
            match = re.search(pattern, text.upper())
            if match:
                self.insight.data['pre_operative']['asa_status'] = f"ASA {match.group(1)}"
                break
    
    def extract_allergies(self, text: str) -> None:
        """Extract allergy information"""
        text_lower = text.lower()
        
        if 'nkda' in text_lower or 'nka' in text_lower:
            self.insight.data['pre_operative']['allergies'] = "NKDA (No Known Drug Allergies)"
            return
        
        for pattern in self.patterns['allergies']:
            match = re.search(pattern, text_lower)
            if match:
                allergy_text = match.group(1).strip()
                if allergy_text and len(allergy_text) > 2:
                    self.insight.data['pre_operative']['allergies'] = allergy_text.title()
                    break
    
    def extract_medications(self, text: str) -> None:
        """Extract medication information with focus on anesthesia-relevant drugs"""
        text_lower = text.lower()
        
        # Look for anticoagulants
        anticoag_found = []
        for drug in self.keywords['anticoagulants']:
            if drug in text_lower:
                anticoag_found.append(drug.title())
        
        if anticoag_found:
            self.insight.data['pre_operative']['medications']['anticoagulants'] = ', '.join(anticoag_found)
        
        # Look for insulin/diabetes medications
        if any(term in text_lower for term in ['insulin', 'metformin', 'glipizide', 'glyburide']):
            diabetes_meds = [term.title() for term in ['insulin', 'metformin', 'glipizide', 'glyburide'] if term in text_lower]
            self.insight.data['pre_operative']['medications']['insulin'] = ', '.join(diabetes_meds)
        
        # Look for cardiac medications
        cardiac_meds = ['beta blocker', 'ace inhibitor', 'lisinopril', 'metoprolol', 'atenolol', 'amlodipine']
        cardiac_found = [med.title() for med in cardiac_meds if med in text_lower]
        if cardiac_found:
            self.insight.data['pre_operative']['medications']['cardiac_meds'] = ', '.join(cardiac_found)
    
    def extract_comorbidities(self, text: str) -> None:
        """Extract relevant comorbidities"""
        text_lower = text.lower()
        
        # Cardiac conditions
        cardiac_conditions = []
        for condition in self.keywords['cardiac_conditions']:
            if condition in text_lower:
                cardiac_conditions.append(condition)
        if cardiac_conditions:
            self.insight.data['pre_operative']['comorbidities']['cardiac'] = ', '.join(cardiac_conditions)
        
        # Pulmonary conditions
        pulmonary_conditions = []
        for condition in self.keywords['pulmonary_conditions']:
            if condition in text_lower:
                pulmonary_conditions.append(condition)
        if pulmonary_conditions:
            self.insight.data['pre_operative']['comorbidities']['pulmonary'] = ', '.join(pulmonary_conditions)
        
        # Renal conditions
        renal_conditions = []
        for condition in self.keywords['renal_conditions']:
            if condition in text_lower:
                renal_conditions.append(condition)
        if renal_conditions:
            self.insight.data['pre_operative']['comorbidities']['renal'] = ', '.join(renal_conditions)
        
        # Diabetes/Endocrine
        if any(term in text_lower for term in self.keywords['diabetes']):
            diabetes_terms = [term for term in self.keywords['diabetes'] if term in text_lower]
            self.insight.data['pre_operative']['comorbidities']['endocrine'] = ', '.join(diabetes_terms)
    
    def extract_lab_values(self, text: str) -> None:
        """Extract relevant laboratory values"""
        text_lower = text.lower()
        
        # Hemoglobin
        hgb_match = re.search(r'(?:hemoglobin|hgb|hb):?\s*(\d+\.?\d*)', text_lower)
        if hgb_match:
            self.insight.data['pre_operative']['laboratory_values']['hemoglobin'] = f"{hgb_match.group(1)} g/dL"
        
        # Platelet count
        plt_match = re.search(r'(?:platelet|plt):?\s*(\d+)', text_lower)
        if plt_match:
            self.insight.data['pre_operative']['laboratory_values']['platelet_count'] = f"{plt_match.group(1)} K/uL"
        
        # INR/PT/PTT
        inr_match = re.search(r'inr:?\s*(\d+\.?\d*)', text_lower)
        if inr_match:
            self.insight.data['pre_operative']['laboratory_values']['inr_pt_ptt'] = f"INR {inr_match.group(1)}"
        
        # Creatinine
        cr_match = re.search(r'(?:creatinine|cr):?\s*(\d+\.?\d*)', text_lower)
        if cr_match:
            self.insight.data['pre_operative']['laboratory_values']['creatinine'] = f"{cr_match.group(1)} mg/dL"
    
    def extract_surgical_plan(self, text: str) -> None:
        """Extract surgical procedure and plan information"""
        text_lower = text.lower()
        
        # Look for procedure mentions
        procedure_patterns = [
            r'(?:procedure|surgery|operation):?\s*([^.\n]+)',
            r'scheduled for:?\s*([^.\n]+)',
            r'undergoing:?\s*([^.\n]+)'
        ]
        
        for pattern in procedure_patterns:
            match = re.search(pattern, text_lower)
            if match:
                procedure = match.group(1).strip()
                if len(procedure) > 3:
                    self.insight.data['surgical_plan']['procedure'] = procedure.title()
                    break
        
        # Look for surgical position
        for position in self.keywords['surgical_positions']:
            if position in text_lower:
                self.insight.data['surgical_plan']['surgical_position'] = position.title()
                break
        
        # Look for duration
        duration_match = re.search(r'(?:duration|time):?\s*(\d+\.?\d*)\s*(?:hours?|hrs?|minutes?|mins?)', text_lower)
        if duration_match:
            self.insight.data['surgical_plan']['estimated_duration'] = duration_match.group(0)
    
    def extract_airway_assessment(self, text: str) -> None:
        """Extract airway assessment information"""
        text_lower = text.lower()
        
        # Mallampati score
        mallampati_match = re.search(r'mallampati:?\s*([1-4IV]+)', text_lower)
        if mallampati_match:
            self.insight.data['pre_operative']['airway_assessment']['mallampati'] = f"Class {mallampati_match.group(1)}"
        
        # Mouth opening
        mouth_match = re.search(r'mouth opening:?\s*(\d+\.?\d*)\s*(?:cm|fingerbreadths?)', text_lower)
        if mouth_match:
            self.insight.data['pre_operative']['airway_assessment']['mouth_opening'] = mouth_match.group(0)
        
        # Look for difficult airway predictors
        if any(term in text_lower for term in ['difficult airway', 'difficult intubation', 'short neck', 'limited neck mobility']):
            self.insight.data['pre_operative']['airway_assessment']['predicted_difficulty'] = "Potentially difficult"
    
    def assess_risks(self, text: str) -> None:
        """Assess anesthesia-related risks"""
        text_lower = text.lower()
        
        # Aspiration risk
        if any(term in text_lower for term in ['not npo', 'recent meal', 'full stomach', 'gastroparesis', 'gerd']):
            self.insight.data['risk_assessment']['aspiration_risk'] = "Elevated"
        elif any(term in text_lower for term in ['npo', 'fasting']):
            self.insight.data['risk_assessment']['aspiration_risk'] = "Standard"
        
        # Cardiac risk
        if any(term in text_lower for term in ['recent mi', 'unstable angina', 'severe aortic stenosis', 'decompensated chf']):
            self.insight.data['risk_assessment']['cardiac_risk'] = "High"
        elif any(term in text_lower for term in self.keywords['cardiac_conditions']):
            self.insight.data['risk_assessment']['cardiac_risk'] = "Moderate"
        
        # Bleeding risk
        if any(term in text_lower for term in ['anticoagulant', 'bleeding disorder', 'thrombocytopenia']):
            self.insight.data['risk_assessment']['bleeding_risk'] = "Elevated"
    
    def process_emr_text(self, emr_text: str) -> Dict[str, Any]:
        """Main method to process EMR text and extract clinical insights"""
        
        # Extract all relevant information
        self.extract_patient_info(emr_text)
        self.extract_asa_status(emr_text)
        self.extract_allergies(emr_text)
        self.extract_medications(emr_text)
        self.extract_comorbidities(emr_text)
        self.extract_lab_values(emr_text)
        self.extract_surgical_plan(emr_text)
        self.extract_airway_assessment(emr_text)
        self.assess_risks(emr_text)
        
        # Add metadata
        self.insight.data['metadata'] = {
            'processed_timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'extraction_confidence': 'Automated extraction - verify critical values'
        }
        
        return self.insight.data


def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python clinical_insight_bot.py '<EMR_TEXT>'")
        print("Or use: python clinical_insight_bot.py --file <filename>")
        return
    
    bot = ClinicalInsightBot()
    
    if sys.argv[1] == '--file' and len(sys.argv) > 2:
        # Read from file
        try:
            with open(sys.argv[2], 'r') as f:
                emr_text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{sys.argv[2]}' not found")
            return
    else:
        # Use command line argument
        emr_text = sys.argv[1]
    
    if not emr_text or emr_text == "<<INSERT PATIENT CHART TEXT>>":
        print("Please provide actual EMR text to process.")
        return
    
    # Process the EMR text
    results = bot.process_emr_text(emr_text)
    
    # Output results as formatted JSON
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 