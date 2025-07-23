#!/usr/bin/env python3
"""
Patient-Facing OAuth Helper for Real Patient Data Access
Uses patient portal credentials for direct patient data access
"""

import os
import json
import webbrowser
from cerner_integration import CernerFHIRClient

def main():
    print("🏥 Clinical Insight Bot - Patient Data Access")
    print("=" * 60)
    
    # Patient-facing configuration
    client_id = "11f19f01-8f14-4425-a603-725bcfeee977"
    
    # Use patient access endpoint instead of provider
    fhir_url = "https://fhir-myrecord.cerner.com/dstu2/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    
    client = CernerFHIRClient(client_id=client_id, fhir_base_url=fhir_url)
    
    # Patient-specific scopes with launch/patient
    patient_scopes = [
        'patient/Patient.read',
        'patient/Observation.read', 
        'patient/Condition.read',
        'patient/MedicationRequest.read',
        'patient/AllergyIntolerance.read',
        'patient/Procedure.read',
        'patient/DiagnosticReport.read',
        'launch/patient',  # This allows patient selection
        'openid',
        'profile',
        'online_access'
    ]
    
    print("\n1. Generating Patient Authorization URL...")
    auth_url, state = client.get_authorization_url(scopes=patient_scopes)
    print("✅ URL Generated!")
    
    print(f"\n🔗 PATIENT AUTHORIZATION URL:")
    print(f"{auth_url}")
    
    print(f"\n📋 STEPS TO FOLLOW:")
    print("1. Copy the URL above")
    print("2. Open it in your browser") 
    print("3. Log in with your PATIENT PORTAL credentials")
    print("4. Select yourself as the patient") 
    print("5. Authorize the app")
    print("6. You'll see: localhost:8080/callback?code=XXXXXX")
    print("7. Copy the code (XXXXXX part)")
    print("8. Return here and enter it")
    
    # Open browser option
    open_browser = input("\n🌐 Open in browser now? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open(auth_url)
        print("✅ Browser opened!")
    
    print("\n" + "="*60)
    print("WAITING FOR YOUR AUTHORIZATION...")
    print("="*60)
    
    # Get authorization code
    auth_code = input("\n📝 Enter your authorization code: ").strip()
    
    if not auth_code:
        print("❌ No code provided. Exiting.")
        return
    
    print("\n2. Exchanging code for access token...")
    try:
        token_response = client.exchange_code_for_token(auth_code)
        print("✅ Access token obtained!")
        print(f"   Patient ID: {token_response.get('patient', 'Not provided')}")
        
        # Get patient data
        patient_id = token_response.get('patient')
        if not patient_id:
            patient_id = input("   Enter patient ID: ").strip()
        
        if patient_id:
            print(f"\n3. Getting your patient data (ID: {patient_id})")
            insights = client.get_clinical_insights(patient_id)
            
            print("\n✅ YOUR CLINICAL INSIGHTS:")
            print("="*40)
            
            # Display key insights
            patient_info = insights.get('patient_info', {})
            print(f"Patient: {patient_info.get('age')} {patient_info.get('gender')}")
            
            pre_op = insights.get('pre_operative', {})
            print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
            print(f"Allergies: {pre_op.get('allergies', 'None')}")
            
            labs = insights.get('laboratory_values', {})
            for key, value in labs.items():
                if value and value != "Not Found":
                    print(f"{key}: {value}")
            
            # Save option
            save = input("\n💾 Save to file? (y/n): ")
            if save.lower() == 'y':
                from datetime import datetime
                filename = f"my_patient_insights_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                with open(filename, 'w') as f:
                    json.dump(insights, f, indent=2)
                print(f"✅ Saved to {filename}")
            
            print("\n🎉 Complete! Your patient data analyzed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your authorization code and try again.")

if __name__ == "__main__":
    main() 