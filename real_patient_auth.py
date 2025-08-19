#!/usr/bin/env python3
"""
Real Patient Data Authorization Script for Cerner FHIR
Guides through OAuth flow to access actual patient data
"""

import os
import json
import webbrowser
from cerner_integration import CernerFHIRClient

def main():
    """Guide user through OAuth flow for real patient data."""
    
    print("🏥 Clinical Insight Bot - Real Patient Data Authorization")
    print("=" * 65)
    
    # Set up client
    client_id = "11f19f01-8f14-4425-a603-725bcfeee977"
    fhir_url = "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    
    client = CernerFHIRClient(
        client_id=client_id,
        fhir_base_url=fhir_url
    )
    
    # Step 1: Generate authorization URL
    print("\n1. Generating OAuth Authorization URL...")
    
    try:
        auth_url, state = client.get_authorization_url()
        print("✅ Authorization URL generated successfully!")
        print(f"   State: {state}")
        print(f"\n🔗 Authorization URL:")
        print(f"{auth_url}")
        
        # Step 2: Guide user through authorization
        print("\n" + "="*65)
        print("2. AUTHORIZATION STEPS:")
        print("="*65)
        print("📋 Please follow these steps:")
        print("1. Copy the URL above")
        print("2. Open it in your browser")
        print("3. Log in with your Cerner patient portal credentials")
        print("4. Authorize the Clinical Insight Bot application")
        print("5. You'll be redirected to localhost:8080/callback?code=...")
        print("6. Copy the 'code' parameter from the URL")
        print("7. Come back here and enter the code")
        
        # Option to auto-open browser
        open_browser = input("\n🌐 Open authorization URL in browser automatically? (y/n): ").lower()
        if open_browser == 'y':
            try:
                webbrowser.open(auth_url)
                print("✅ Browser opened. Complete authorization and return here.")
            except Exception as e:
                print(f"❌ Could not open browser: {e}")
                print("Please manually copy and open the URL above.")
        
        # Step 3: Get authorization code
        print("\n" + "="*65)
        print("3. ENTER AUTHORIZATION CODE:")
        print("="*65)
        print("After completing authorization, you'll see a URL like:")
        print("http://localhost:8080/callback?code=AUTHORIZATION_CODE&state=...")
        print("\nCopy just the AUTHORIZATION_CODE part (after code=)")
        
        auth_code = input("\n📝 Enter your authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided. Exiting.")
            return
        
        # Step 4: Exchange code for token
        print("\n4. Exchanging Authorization Code for Access Token...")
        
        try:
            token_response = client.exchange_code_for_token(auth_code)
            print("✅ Access token obtained successfully!")
            print(f"   Token expires in: {token_response.get('expires_in', 'Unknown')} seconds")
            print(f"   Patient ID in context: {token_response.get('patient', 'Not provided')}")
            
            # Step 5: Get real patient data
            print("\n5. Accessing Real Patient Data...")
            
            patient_id = token_response.get('patient')
            if patient_id:
                print(f"   Using patient ID from token context: {patient_id}")
                patient_data = client.get_patient_data(patient_id)
            else:
                # Ask for patient ID if not in context
                patient_id = input("   Enter patient ID to access: ").strip()
                if patient_id:
                    patient_data = client.get_patient_data(patient_id)
                else:
                    print("❌ No patient ID provided.")
                    return
            
            print("✅ Patient data retrieved successfully!")
            
            # Step 6: Convert to text and generate insights
            print("\n6. Converting FHIR Data to Clinical Text...")
            patient_text = client.convert_fhir_to_text(patient_data)
            
            print("\n7. Generating Clinical Insights...")
            insights = client.get_clinical_insights(patient_id)
            
            # Display results
            print("\n" + "="*65)
            print("CLINICAL INSIGHTS - REAL PATIENT DATA")
            print("="*65)
            
            # Patient info
            patient_info = insights.get('patient_info', {})
            print(f"Patient: {patient_info.get('age', 'Unknown')} {patient_info.get('gender', 'Unknown')}")
            
            # Key insights
            pre_op = insights.get('pre_operative', {})
            print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
            print(f"Allergies: {pre_op.get('allergies', 'None found')}")
            
            intra_op = insights.get('intra_operative', {})
            print(f"Recommended Monitoring: {intra_op.get('monitoring', 'Standard')}")
            
            # Lab values
            labs = insights.get('laboratory_values', {})
            if labs:
                print("\nLaboratory Values:")
                for key, value in labs.items():
                    if value and value != "Not Found":
                        print(f"  {key}: {value}")
            
            # Save results
            save_results = input("\n💾 Save results to file? (y/n): ").lower()
            if save_results == 'y':
                from datetime import datetime
                filename = f"real_patient_insights_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(insights, f, indent=2)
                print(f"✅ Results saved to {filename}")
            
            print("\n🎉 Real patient data analysis complete!")
            
        except Exception as e:
            print(f"❌ Error during token exchange: {e}")
            print("\nTroubleshooting:")
            print("- Verify the authorization code is correct")
            print("- Make sure you didn't include extra characters")
            print("- The code may have expired (try authorization again)")
    
    except Exception as e:
        print(f"❌ Error generating authorization URL: {e}")

if __name__ == "__main__":
    main() 