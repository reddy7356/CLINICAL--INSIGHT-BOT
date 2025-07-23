#!/usr/bin/env python3
"""
Direct Patient Data Access using Test Patient IDs
Bypasses OAuth for demonstration with sandbox test patients
"""

import requests
import json
from clinical_insight_bot import ClinicalInsightBot

def get_test_patient_data(patient_id):
    """Get test patient data directly from Cerner open FHIR endpoint."""
    
    base_url = "https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    headers = {
        'Accept': 'application/fhir+json'
    }
    
    patient_data = {}
    
    try:
        # Get Patient resource
        print(f"Getting patient data for ID: {patient_id}")
        patient_url = f"{base_url}/Patient/{patient_id}"
        response = requests.get(patient_url, headers=headers, timeout=30)
        if response.status_code == 200:
            patient_data['patient'] = response.json()
            print("✅ Patient data retrieved")
        else:
            print(f"❌ Patient data failed: {response.status_code}")
            return None
        
        # Get Observations
        print("Getting observations...")
        obs_url = f"{base_url}/Observation?patient={patient_id}&_count=50"
        response = requests.get(obs_url, headers=headers, timeout=30)
        if response.status_code == 200:
            obs_bundle = response.json()
            patient_data['observations'] = obs_bundle.get('entry', [])
            print(f"✅ Found {len(patient_data['observations'])} observations")
        
        # Get Conditions
        print("Getting conditions...")
        cond_url = f"{base_url}/Condition?patient={patient_id}&_count=50"
        response = requests.get(cond_url, headers=headers, timeout=30)
        if response.status_code == 200:
            cond_bundle = response.json()
            patient_data['conditions'] = cond_bundle.get('entry', [])
            print(f"✅ Found {len(patient_data['conditions'])} conditions")
        
        # Get Medications
        print("Getting medication requests...")
        med_url = f"{base_url}/MedicationRequest?patient={patient_id}&_count=50"
        response = requests.get(med_url, headers=headers, timeout=30)
        if response.status_code == 200:
            med_bundle = response.json()
            patient_data['medications'] = med_bundle.get('entry', [])
            print(f"✅ Found {len(patient_data['medications'])} medications")
        
        # Get Allergies
        print("Getting allergies...")
        allergy_url = f"{base_url}/AllergyIntolerance?patient={patient_id}&_count=50"
        response = requests.get(allergy_url, headers=headers, timeout=30)
        if response.status_code == 200:
            allergy_bundle = response.json()
            patient_data['allergies'] = allergy_bundle.get('entry', [])
            print(f"✅ Found {len(patient_data['allergies'])} allergies")
        
        # Get Procedures
        print("Getting procedures...")
        proc_url = f"{base_url}/Procedure?patient={patient_id}&_count=50"
        response = requests.get(proc_url, headers=headers, timeout=30)
        if response.status_code == 200:
            proc_bundle = response.json()
            patient_data['procedures'] = proc_bundle.get('entry', [])
            print(f"✅ Found {len(patient_data['procedures'])} procedures")
        
        return patient_data
        
    except Exception as e:
        print(f"❌ Error getting patient data: {e}")
        return None

def convert_fhir_to_text(patient_data):
    """Convert FHIR patient data to readable text."""
    
    text_sections = []
    
    # Patient demographics
    if 'patient' in patient_data:
        patient = patient_data['patient']
        name = "Unknown"
        if 'name' in patient and patient['name']:
            given = ' '.join(patient['name'][0].get('given', []))
            family = ' '.join(patient['name'][0].get('family', [])) if isinstance(patient['name'][0].get('family'), list) else patient['name'][0].get('family', '')
            name = f"{given} {family}".strip()
        
        birth_date = patient.get('birthDate', 'Unknown')
        gender = patient.get('gender', 'Unknown')
        
        # Calculate age
        age = "Unknown"
        if birth_date != 'Unknown':
            try:
                from datetime import datetime
                birth_year = int(birth_date.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
            except:
                pass
        
        text_sections.append(f"PATIENT: {name}")
        text_sections.append(f"AGE: {age} years old")
        text_sections.append(f"GENDER: {gender.title()}")
        text_sections.append("")
    
    # Conditions
    if 'conditions' in patient_data and patient_data['conditions']:
        text_sections.append("PAST MEDICAL HISTORY:")
        for entry in patient_data['conditions']:
            resource = entry.get('resource', {})
            if 'code' in resource and 'text' in resource['code']:
                condition = resource['code']['text']
                text_sections.append(f"- {condition}")
        text_sections.append("")
    
    # Medications
    if 'medications' in patient_data and patient_data['medications']:
        text_sections.append("MEDICATIONS:")
        for entry in patient_data['medications']:
            resource = entry.get('resource', {})
            med_name = "Unknown medication"
            if 'medicationCodeableConcept' in resource and 'text' in resource['medicationCodeableConcept']:
                med_name = resource['medicationCodeableConcept']['text']
            elif 'medicationReference' in resource and 'display' in resource['medicationReference']:
                med_name = resource['medicationReference']['display']
            
            dosage = ""
            if 'dosageInstruction' in resource and resource['dosageInstruction']:
                dosage_text = resource['dosageInstruction'][0].get('text', '')
                if dosage_text:
                    dosage = f" - {dosage_text}"
            
            text_sections.append(f"- {med_name}{dosage}")
        text_sections.append("")
    
    # Allergies
    if 'allergies' in patient_data and patient_data['allergies']:
        text_sections.append("ALLERGIES:")
        for entry in patient_data['allergies']:
            resource = entry.get('resource', {})
            allergen = "Unknown allergen"
            if 'code' in resource and 'text' in resource['code']:
                allergen = resource['code']['text']
            
            reaction = ""
            if 'reaction' in resource and resource['reaction']:
                manifestations = []
                for react in resource['reaction']:
                    if 'manifestation' in react:
                        for manif in react['manifestation']:
                            if 'text' in manif:
                                manifestations.append(manif['text'])
                if manifestations:
                    reaction = f" ({', '.join(manifestations)})"
            
            text_sections.append(f"- {allergen}{reaction}")
        text_sections.append("")
    
    # Lab values (from observations)
    if 'observations' in patient_data and patient_data['observations']:
        text_sections.append("LABORATORY VALUES:")
        for entry in patient_data['observations']:
            resource = entry.get('resource', {})
            if 'code' in resource and 'text' in resource['code']:
                test_name = resource['code']['text']
                value = ""
                if 'valueQuantity' in resource:
                    val = resource['valueQuantity'].get('value', '')
                    unit = resource['valueQuantity'].get('unit', '')
                    value = f": {val} {unit}"
                elif 'valueString' in resource:
                    value = f": {resource['valueString']}"
                
                if value:
                    text_sections.append(f"{test_name}{value}")
        text_sections.append("")
    
    return '\n'.join(text_sections)

def main():
    print("🏥 Clinical Insight Bot - Direct Test Patient Access")
    print("=" * 60)
    
    # Test patient IDs from Cerner sandbox
    test_patients = {
        "12724066": "Adult patient with comprehensive data",
        "12724067": "Pediatric patient", 
        "12724068": "Patient with multiple conditions"
    }
    
    print("\n📋 Available Test Patients:")
    for pid, description in test_patients.items():
        print(f"  {pid}: {description}")
    
    patient_id = input("\nEnter patient ID to analyze (or press Enter for 12724066): ").strip()
    if not patient_id:
        patient_id = "12724066"
    
    print(f"\n🔍 Accessing data for patient {patient_id}...")
    
    # Get patient data directly
    patient_data = get_test_patient_data(patient_id)
    
    if not patient_data:
        print("❌ Failed to get patient data")
        return
    
    print("\n📝 Converting FHIR data to text...")
    patient_text = convert_fhir_to_text(patient_data)
    
    print("\n" + "="*60)
    print("PATIENT DATA (TEXT FORMAT)")
    print("="*60)
    print(patient_text)
    
    print("\n🧠 Generating clinical insights...")
    
    # Initialize Clinical Insight Bot
    insight_bot = ClinicalInsightBot()
    insights = insight_bot.process_emr_text(patient_text)
    
    print("\n" + "="*60)
    print("CLINICAL INSIGHTS FOR ANESTHESIA")
    print("="*60)
    
    # Display insights
    patient_info = insights.get('patient_info', {})
    print(f"Patient: {patient_info.get('age', 'Unknown')} {patient_info.get('gender', 'Unknown')}")
    
    pre_op = insights.get('pre_operative', {})
    print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
    print(f"Allergies: {pre_op.get('allergies', 'None found')}")
    
    # Risk factors
    cardiac = pre_op.get('cardiac_risk', '')
    if cardiac:
        print(f"Cardiac Risk: {cardiac}")
    
    respiratory = pre_op.get('respiratory_risk', '')
    if respiratory:
        print(f"Respiratory Risk: {respiratory}")
    
    renal = pre_op.get('renal_risk', '')
    if renal:
        print(f"Renal Risk: {renal}")
    
    # Lab values
    labs = insights.get('laboratory_values', {})
    if labs:
        print(f"\nKey Lab Values:")
        for key, value in labs.items():
            if value and value != "Not Found":
                print(f"  {key}: {value}")
    
    # Save results
    save = input("\n💾 Save results to file? (y/n): ")
    if save.lower() == 'y':
        from datetime import datetime
        filename = f"patient_insights_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'patient_data': patient_text,
                'insights': insights
            }, f, indent=2)
        print(f"✅ Saved to {filename}")
    
    print("\n🎉 Analysis complete! Real patient data processed successfully.")

if __name__ == "__main__":
    main() 