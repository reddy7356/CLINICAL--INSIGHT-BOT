#!/usr/bin/env python3
"""
Example script demonstrating Cerner FHIR integration with Clinical Insight Bot
"""

import os
import json
from cerner_integration import CernerFHIRClient, start_oauth_flow


def main():
    """Example integration workflow with Cerner FHIR."""
    
    print("🏥 Clinical Insight Bot - Cerner FHIR Integration Example")
    print("=" * 60)
    
    # Step 1: Configuration
    print("\n1. Checking Configuration...")
    
    client_id = os.getenv('CERNER_CLIENT_ID')
    client_secret = os.getenv('CERNER_CLIENT_SECRET')  # Optional for public clients
    fhir_url = os.getenv('CERNER_FHIR_URL')
    
    if not client_id:
        print("❌ Missing CERNER_CLIENT_ID environment variable")
        print("Please set your environment variables:")
        print("export CERNER_CLIENT_ID='your-client-id-from-cerner'")
        print("export CERNER_FHIR_URL='https://fhir-ehr-code.cerner.com/r4/tenant-id'")
        return
    
    if not fhir_url:
        # Use Cerner's sandbox environment as default
        fhir_url = "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
        print(f"⚠️  Using default sandbox FHIR URL: {fhir_url}")
    
    print(f"✅ Client ID: {client_id[:8]}...")
    print(f"✅ FHIR URL: {fhir_url}")
    
    # Step 2: Initialize FHIR Client
    print("\n2. Initializing FHIR Client...")
    
    client = CernerFHIRClient(
        client_id=client_id,
        client_secret=client_secret,
        fhir_base_url=fhir_url
    )
    
    # Step 3: Start OAuth Flow
    print("\n3. Starting OAuth Authorization Flow...")
    
    try:
        # Discover SMART configuration
        smart_config = client.discover_smart_configuration()
        print("✅ SMART configuration discovered")
        print(f"   Authorization Endpoint: {smart_config.get('authorization_endpoint', 'Not found')}")
        print(f"   Token Endpoint: {smart_config.get('token_endpoint', 'Not found')}")
        
        # Generate authorization URL
        auth_url, state = client.get_authorization_url()
        print("✅ Authorization URL generated")
        print(f"   State: {state}")
        print(f"   URL: {auth_url}")
        
        print("\n📋 Next Steps:")
        print("1. Visit the authorization URL above")
        print("2. Log in and authorize the application")
        print("3. Copy the authorization code from the callback")
        print("4. Use the code with client.exchange_code_for_token(code)")
        
        # Interactive demonstration
        print("\n" + "="*60)
        print("Interactive Demo (optional)")
        print("="*60)
        
        demo_choice = input("\nWould you like to see a demo with sample data? (y/n): ").lower()
        
        if demo_choice == 'y':
            demonstrate_with_sample_data(client)
            
    except Exception as e:
        print(f"❌ Error during OAuth setup: {e}")
        print("\nTroubleshooting tips:")
        print("- Verify your client ID is correct")
        print("- Check that your app is registered in Cerner Code Console")
        print("- Ensure the FHIR URL is accessible")


def demonstrate_with_sample_data(client):
    """Demonstrate functionality with sample FHIR data."""
    
    print("\n4. Sample Data Demonstration...")
    
    # Sample FHIR patient data (synthetic)
    sample_patient_data = {
        'patient': {
            'name': [{'given': ['Jane'], 'family': 'Smith'}],
            'birthDate': '1955-02-15',
            'gender': 'female'
        },
        'conditions': [
            {
                'code': {
                    'text': 'Essential hypertension'
                }
            },
            {
                'code': {
                    'text': 'Type 2 diabetes mellitus'
                }
            },
            {
                'code': {
                    'text': 'Chronic kidney disease stage 3'
                }
            }
        ],
        'medications': [
            {
                'medicationCodeableConcept': {
                    'text': 'Metoprolol'
                },
                'dosageInstruction': [
                    {
                        'text': '50mg twice daily'
                    }
                ]
            },
            {
                'medicationCodeableConcept': {
                    'text': 'Insulin glargine'
                },
                'dosageInstruction': [
                    {
                        'text': '24 units nightly'
                    }
                ]
            }
        ],
        'allergies': [
            {
                'code': {
                    'text': 'Penicillin'
                },
                'reaction': [
                    {
                        'manifestation': [
                            {
                                'text': 'rash'
                            }
                        ]
                    }
                ]
            }
        ],
        'observations': [
            {
                'code': {
                    'text': 'Hemoglobin'
                },
                'valueQuantity': {
                    'value': 11.8,
                    'unit': 'g/dL'
                }
            },
            {
                'code': {
                    'text': 'Creatinine'
                },
                'valueQuantity': {
                    'value': 1.4,
                    'unit': 'mg/dL'
                }
            }
        ]
    }
    
    print("✅ Using sample patient data...")
    
    # Convert FHIR data to text
    patient_text = client.convert_fhir_to_text(sample_patient_data)
    print("\n5. Converted FHIR Data to Text:")
    print("-" * 40)
    print(patient_text)
    
    # Process with Clinical Insight Bot
    print("\n6. Processing with Clinical Insight Bot...")
    insights = client.insight_bot.process_emr_text(patient_text)
    
    print("✅ Clinical insights generated!")
    
    # Display key insights
    print("\n7. Key Anesthesia Insights:")
    print("-" * 40)
    
    patient_info = insights.get('patient_info', {})
    print(f"Patient: {patient_info.get('age', 'Unknown age')} {patient_info.get('gender', 'Unknown gender')}")
    
    pre_op = insights.get('pre_operative', {})
    print(f"ASA Status: {pre_op.get('asa_status', 'Not determined')}")
    print(f"Allergies: {pre_op.get('allergies', 'None found')}")
    
    medications = pre_op.get('medications', {})
    print(f"Cardiac Meds: {medications.get('cardiac_meds', 'None found')}")
    print(f"Insulin: {medications.get('insulin', 'None found')}")
    
    comorbidities = pre_op.get('comorbidities', {})
    print(f"Cardiac: {comorbidities.get('cardiac', 'None found')}")
    print(f"Renal: {comorbidities.get('renal', 'None found')}")
    print(f"Endocrine: {comorbidities.get('endocrine', 'None found')}")
    
    lab_values = pre_op.get('laboratory_values', {})
    print(f"Hemoglobin: {lab_values.get('hemoglobin', 'Not found')}")
    print(f"Creatinine: {lab_values.get('creatinine', 'Not found')}")
    
    risks = insights.get('risk_assessment', {})
    print(f"Cardiac Risk: {risks.get('cardiac_risk', 'Not assessed')}")
    
    # Option to save results
    save_choice = input("\nSave results to file? (y/n): ").lower()
    if save_choice == 'y':
        with open('sample_insights.json', 'w') as f:
            json.dump(insights, f, indent=2)
        print("✅ Results saved to sample_insights.json")


def example_with_real_authorization():
    """Example showing real authorization flow completion."""
    
    print("\n" + "="*60)
    print("Real Authorization Example")
    print("="*60)
    
    print("""
This example shows how to complete the OAuth flow with a real authorization code:

```python
from cerner_integration import CernerFHIRClient

# Initialize client
client = CernerFHIRClient(
    client_id='your-client-id',
    fhir_base_url='https://fhir-ehr-code.cerner.com/r4/tenant-id'
)

# After user authorization, you receive a code
authorization_code = 'auth-code-from-callback'

# Exchange for access token
token_response = client.exchange_code_for_token(authorization_code)

# Now you can access patient data
patient_data = client.get_patient_data(patient_id='12724066')

# Get clinical insights
insights = client.get_clinical_insights(patient_id='12724066')

print(json.dumps(insights, indent=2))
```

Test Patient IDs in Cerner Sandbox:
- 12724066: Adult patient with comprehensive data
- 12724067: Pediatric patient
- 12724068: Patient with multiple conditions
""")


if __name__ == "__main__":
    main()
    
    print("\n" + "="*60)
    print("For more information, see:")
    print("- cerner_integration_guide.md (comprehensive guide)")
    print("- cerner_integration.py (full implementation)")
    print("- Cerner FHIR documentation: https://fhir.cerner.com/")
    print("="*60) 