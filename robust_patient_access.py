#!/usr/bin/env python3
"""
Robust Patient Data Access with timeout handling
Gets as much data as possible even if some requests fail
"""

import requests
import json
from clinical_insight_bot import ClinicalInsightBot

def get_patient_resource(base_url, headers, patient_id, resource_type, query_params=""):
    """Get a specific FHIR resource with error handling."""
    try:
        if resource_type == "Patient":
            url = f"{base_url}/{resource_type}/{patient_id}"
        else:
            url = f"{base_url}/{resource_type}?patient={patient_id}&_count=20{query_params}"
        
        print(f"  Getting {resource_type}...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if resource_type == "Patient":
                return data
            else:
                entries = data.get('entry', [])
                print(f"  ✅ Found {len(entries)} {resource_type}")
                return entries
        else:
            print(f"  ❌ {resource_type} failed: HTTP {response.status_code}")
            return []
            
    except requests.Timeout:
        print(f"  ⚠️ {resource_type} timed out, skipping...")
        return []
    except Exception as e:
        print(f"  ❌ {resource_type} error: {str(e)[:50]}...")
        return []

def get_robust_patient_data(patient_id):
    """Get patient data with robust error handling."""
    
    base_url = "https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    headers = {'Accept': 'application/fhir+json'}
    
    print(f"🔍 Accessing data for patient {patient_id}...")
    
    patient_data = {}
    
    # Get Patient (required)
    patient = get_patient_resource(base_url, headers, patient_id, "Patient")
    if not patient:
        print("❌ Could not get basic patient data")
        return None
    
    patient_data['patient'] = patient
    print("✅ Patient demographics retrieved")
    
    # Try to get other resources (optional)
    resources_to_get = [
        ("Observation", "observations"),
        ("Condition", "conditions"), 
        ("MedicationRequest", "medications"),
        ("AllergyIntolerance", "allergies"),
        ("Procedure", "procedures")
    ]
    
    for resource_type, key in resources_to_get:
        result = get_patient_resource(base_url, headers, patient_id, resource_type)
        patient_data[key] = result
    
    # Summary
    total_resources = sum(len(v) if isinstance(v, list) else 1 for v in patient_data.values())
    print(f"\n✅ Retrieved {total_resources} total resources")
    
    return patient_data

def convert_fhir_to_text_robust(patient_data):
    """Convert FHIR data to text with robust error handling."""
    
    text_sections = []
    
    try:
        # Patient demographics
        if 'patient' in patient_data:
            patient = patient_data['patient']
            
            # Name
            name = "Unknown Patient"
            if 'name' in patient and patient['name']:
                name_parts = []
                first_name = patient['name'][0]
                if 'given' in first_name:
                    name_parts.extend(first_name['given'])
                if 'family' in first_name:
                    if isinstance(first_name['family'], list):
                        name_parts.extend(first_name['family'])
                    else:
                        name_parts.append(first_name['family'])
                name = ' '.join(name_parts) if name_parts else "Unknown Patient"
            
            # Age calculation
            age = "Unknown"
            birth_date = patient.get('birthDate', '')
            if birth_date:
                try:
                    from datetime import datetime
                    birth_year = int(birth_date.split('-')[0])
                    age = datetime.now().year - birth_year
                except:
                    age = "Unknown"
            
            gender = patient.get('gender', 'unknown').title()
            
            text_sections.extend([
                f"PATIENT: {name}",
                f"AGE: {age} years old", 
                f"GENDER: {gender}",
                ""
            ])
    except Exception as e:
        text_sections.extend(["PATIENT: Data parsing error", ""])
    
    # Conditions
    try:
        if 'conditions' in patient_data and patient_data['conditions']:
            text_sections.append("PAST MEDICAL HISTORY:")
            for entry in patient_data['conditions'][:10]:  # Limit to 10
                resource = entry.get('resource', {})
                condition_text = "Unknown condition"
                
                if 'code' in resource:
                    if 'text' in resource['code']:
                        condition_text = resource['code']['text']
                    elif 'coding' in resource['code'] and resource['code']['coding']:
                        for coding in resource['code']['coding']:
                            if 'display' in coding:
                                condition_text = coding['display']
                                break
                
                text_sections.append(f"- {condition_text}")
            text_sections.append("")
    except Exception as e:
        text_sections.extend(["PAST MEDICAL HISTORY: Error parsing conditions", ""])
    
    # Medications
    try:
        if 'medications' in patient_data and patient_data['medications']:
            text_sections.append("MEDICATIONS:")
            for entry in patient_data['medications'][:10]:  # Limit to 10
                resource = entry.get('resource', {})
                med_name = "Unknown medication"
                
                # Try different ways to get medication name
                if 'medicationCodeableConcept' in resource:
                    med_concept = resource['medicationCodeableConcept']
                    if 'text' in med_concept:
                        med_name = med_concept['text']
                    elif 'coding' in med_concept and med_concept['coding']:
                        for coding in med_concept['coding']:
                            if 'display' in coding:
                                med_name = coding['display']
                                break
                
                # Add dosage if available
                dosage = ""
                if 'dosageInstruction' in resource and resource['dosageInstruction']:
                    dose_instruction = resource['dosageInstruction'][0]
                    if 'text' in dose_instruction:
                        dosage = f" - {dose_instruction['text']}"
                
                text_sections.append(f"- {med_name}{dosage}")
            text_sections.append("")
    except Exception as e:
        text_sections.extend(["MEDICATIONS: Error parsing medications", ""])
    
    # Allergies
    try:
        if 'allergies' in patient_data and patient_data['allergies']:
            text_sections.append("ALLERGIES:")
            for entry in patient_data['allergies'][:5]:  # Limit to 5
                resource = entry.get('resource', {})
                allergen = "Unknown allergen"
                
                if 'code' in resource and 'text' in resource['code']:
                    allergen = resource['code']['text']
                elif 'code' in resource and 'coding' in resource['code']:
                    for coding in resource['code']['coding']:
                        if 'display' in coding:
                            allergen = coding['display']
                            break
                
                reaction = ""
                if 'reaction' in resource and resource['reaction']:
                    reactions = []
                    for react in resource['reaction'][:2]:  # Limit reactions
                        if 'manifestation' in react:
                            for manif in react['manifestation']:
                                if 'text' in manif:
                                    reactions.append(manif['text'])
                                elif 'coding' in manif:
                                    for coding in manif['coding']:
                                        if 'display' in coding:
                                            reactions.append(coding['display'])
                                            break
                    if reactions:
                        reaction = f" ({', '.join(reactions)})"
                
                text_sections.append(f"- {allergen}{reaction}")
            text_sections.append("")
    except Exception as e:
        text_sections.extend(["ALLERGIES: Error parsing allergies", ""])
    
    # Key Lab Values (from observations)
    try:
        if 'observations' in patient_data and patient_data['observations']:
            text_sections.append("LABORATORY VALUES:")
            lab_count = 0
            
            for entry in patient_data['observations']:
                if lab_count >= 15:  # Limit to 15 labs
                    break
                    
                resource = entry.get('resource', {})
                if 'code' in resource and 'valueQuantity' in resource:
                    test_name = "Unknown test"
                    
                    if 'text' in resource['code']:
                        test_name = resource['code']['text']
                    elif 'coding' in resource['code']:
                        for coding in resource['code']['coding']:
                            if 'display' in coding:
                                test_name = coding['display']
                                break
                    
                    value_qty = resource['valueQuantity']
                    value = value_qty.get('value', '')
                    unit = value_qty.get('unit', '')
                    
                    if value:
                        text_sections.append(f"{test_name}: {value} {unit}".strip())
                        lab_count += 1
            
            if lab_count == 0:
                text_sections.append("No quantitative lab values found")
            text_sections.append("")
    except Exception as e:
        text_sections.extend(["LABORATORY VALUES: Error parsing lab values", ""])
    
    return '\n'.join(text_sections)

def main():
    print("🏥 Clinical Insight Bot - Robust Patient Data Access")
    print("=" * 65)
    
    # Default to the comprehensive test patient
    patient_id = "12724066"
    
    print(f"\n📋 Analyzing Patient ID: {patient_id}")
    print("   (Adult patient with comprehensive data)")
    
    # Get patient data
    patient_data = get_robust_patient_data(patient_id)
    
    if not patient_data:
        print("❌ Failed to get any patient data")
        return
    
    print("\n📝 Converting FHIR data to clinical text...")
    patient_text = convert_fhir_to_text_robust(patient_data)
    
    print("\n" + "="*65)
    print("PATIENT DATA (CLINICAL TEXT)")
    print("="*65)
    print(patient_text)
    
    print("\n🧠 Generating anesthesia insights...")
    
    # Process with Clinical Insight Bot
    try:
        insight_bot = ClinicalInsightBot()
        insights = insight_bot.process_emr_text(patient_text)
        
        print("\n" + "="*65)
        print("CLINICAL INSIGHTS FOR ANESTHESIA PLANNING")
        print("="*65)
        
        # Patient info
        patient_info = insights.get('patient_info', {})
        print(f"Patient: {patient_info.get('age', 'Unknown')} {patient_info.get('gender', 'Unknown')}")
        
        # Pre-operative assessment
        pre_op = insights.get('pre_operative', {})
        print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
        
        allergies = pre_op.get('allergies', '')
        if allergies and allergies != 'None found':
            print(f"Allergies: {allergies}")
        
        # Risk stratification
        cardiac_risk = pre_op.get('cardiac_risk', '')
        if cardiac_risk:
            print(f"Cardiac Risk: {cardiac_risk}")
        
        respiratory_risk = pre_op.get('respiratory_risk', '')
        if respiratory_risk:
            print(f"Respiratory Risk: {respiratory_risk}")
        
        renal_risk = pre_op.get('renal_risk', '')
        if renal_risk:
            print(f"Renal Risk: {renal_risk}")
        
        # Key lab values
        labs = insights.get('laboratory_values', {})
        important_labs = {k: v for k, v in labs.items() 
                         if v and v != "Not Found" and 
                         k.lower() in ['hemoglobin', 'creatinine', 'platelets', 'glucose']}
        
        if important_labs:
            print(f"\nKey Lab Values:")
            for lab, value in important_labs.items():
                print(f"  {lab}: {value}")
        
        # Recommendations
        intra_op = insights.get('intra_operative', {})
        monitoring = intra_op.get('monitoring', '')
        if monitoring and monitoring != 'Standard':
            print(f"\nRecommended Monitoring: {monitoring}")
        
        precautions = intra_op.get('precautions', '')
        if precautions:
            print(f"Precautions: {precautions}")
        
        print("\n🎉 SUCCESS! Real Cerner patient data analyzed for anesthesia planning!")
        
        # Save option
        save = input("\n💾 Save complete analysis to file? (y/n): ")
        if save.lower() == 'y':
            from datetime import datetime
            filename = f"cerner_patient_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'patient_id': patient_id,
                    'raw_text': patient_text,
                    'insights': insights,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            print(f"✅ Complete analysis saved to {filename}")
        
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        print("But we successfully retrieved real patient data from Cerner!")

if __name__ == "__main__":
    main() 