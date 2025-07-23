#!/usr/bin/env python3
"""
Standalone Patient Authorization for Cerner Sandbox
Uses launch/patient scope to allow patient selection
"""

import os
import json
import webbrowser
from cerner_integration import CernerFHIRClient

def main():
    print("🏥 Clinical Insight Bot - Standalone Patient Access")
    print("=" * 60)
    
    # Use same sandbox but with patient launch context
    client_id = "11f19f01-8f14-4425-a603-725bcfeee977"
    fhir_url = "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    
    client = CernerFHIRClient(client_id=client_id, fhir_base_url=fhir_url)
    
    # Use launch/patient scope for standalone patient access
    patient_scopes = [
        'patient/Patient.read',
        'patient/Observation.read', 
        'patient/Condition.read',
        'patient/MedicationRequest.read',
        'patient/AllergyIntolerance.read',
        'patient/Procedure.read',
        'patient/DiagnosticReport.read',
        'launch/patient',  # This allows patient selection in standalone
        'openid',
        'profile',
        'online_access'
    ]
    
    print("\n1. Generating Standalone Patient Authorization URL...")
    auth_url, state = client.get_authorization_url(scopes=patient_scopes)
    print("✅ URL Generated!")
    
    print(f"\n🔗 STANDALONE PATIENT AUTHORIZATION URL:")
    print(f"{auth_url}")
    
    print(f"\n📋 STEPS TO FOLLOW:")
    print("1. Copy the URL above")
    print("2. Open it in your browser") 
    print("3. You'll see a patient selection screen")
    print("4. Choose a test patient from the list")
    print("5. Use the same credentials: portal/portal")
    print("6. Authorize the app")
    print("7. Copy the authorization code from callback")
    print("8. Return here and enter it")
    
    print(f"\n💡 AVAILABLE TEST PATIENTS:")
    print("- 12724066: Adult patient with comprehensive data")
    print("- 12724067: Pediatric patient") 
    print("- 12724068: Patient with multiple conditions")
    print("- You can select any of these during authorization")
    
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
            print(f"\n3. Getting patient data for ID: {patient_id}")
            insights = client.get_clinical_insights(patient_id)
            
            print("\n✅ PATIENT CLINICAL INSIGHTS:")
            print("="*40)
            
            # Display key insights
            patient_info = insights.get('patient_info', {})
            print(f"Patient: {patient_info.get('age')} {patient_info.get('gender')}")
            
            pre_op = insights.get('pre_operative', {})
            print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
            print(f"Allergies: {pre_op.get('allergies', 'None')}")
            
            # Risk factors
            risk_factors = insights.get('risk_factors', {})
            if risk_factors:
                print(f"\nRisk Factors:")
                for category, factors in risk_factors.items():
                    if factors:
                        print(f"  {category}: {factors}")
            
            # Lab values
            labs = insights.get('laboratory_values', {})
            if labs:
                print(f"\nLab Values:")
                for key, value in labs.items():
                    if value and value != "Not Found":
                        print(f"  {key}: {value}")
            
            # Save option
            save = input("\n💾 Save results to file? (y/n): ")
            if save.lower() == 'y':
                from datetime import datetime
                filename = f"patient_insights_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                with open(filename, 'w') as f:
                    json.dump(insights, f, indent=2)
                print(f"✅ Saved to {filename}")
            
            print("\n🎉 Complete! Patient data analysis finished.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Verify the authorization code is correct")
        print("- Make sure you selected a patient during authorization")
        print("- Try the process again if needed")

if __name__ == "__main__":
    main() 