#!/usr/bin/env python3
"""
EPIC FHIR Integration Example
Demonstrates how to connect to EPIC's FHIR APIs and extract clinical insights.
"""

import os
import json
from epic_integration import EpicFHIRClient, start_epic_oauth_flow, test_epic_connection


def main():
    print("=== EPIC FHIR Integration Example ===\n")
    
    # Test connection first
    print("1. Testing connection to EPIC FHIR sandbox...")
    if test_epic_connection():
        print("✓ Successfully connected to EPIC FHIR server!")
    else:
        print("✗ Failed to connect to EPIC FHIR server")
        print("Please check your internet connection and try again.")
        return
    
    # Get client credentials
    client_id = os.getenv('EPIC_CLIENT_ID')
    client_secret = os.getenv('EPIC_CLIENT_SECRET')
    fhir_base_url = os.getenv('EPIC_FHIR_URL', 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/')
    
    if not client_id:
        print("\n2. Setting up EPIC credentials...")
        print("You need to register your application with EPIC first.")
        print("Visit: https://fhir.epic.com/")
        print("After registration, set these environment variables:")
        print("  export EPIC_CLIENT_ID='your_client_id'")
        print("  export EPIC_CLIENT_SECRET='your_client_secret'  # if confidential client")
        print("  export EPIC_FHIR_URL='your_fhir_base_url'")
        
        # For demo purposes, let's use a test client ID
        client_id = input("\nEnter your EPIC Client ID (or press Enter for demo): ").strip()
        if not client_id:
            print("Using demo mode without real authentication...")
            demo_mode()
            return
    
    print(f"\n2. Initializing EPIC FHIR client...")
    print(f"   Client ID: {client_id}")
    print(f"   FHIR Base URL: {fhir_base_url}")
    
    try:
        # Initialize client
        client = EpicFHIRClient(
            client_id=client_id,
            client_secret=client_secret,
            fhir_base_url=fhir_base_url
        )
        
        # Test SMART configuration discovery
        print("\n3. Discovering EPIC SMART configuration...")
        smart_config = client.discover_smart_configuration()
        print("✓ SMART configuration discovered successfully")
        
        # Start OAuth flow
        print("\n4. Starting OAuth authorization flow...")
        client_instance, state = start_epic_oauth_flow(
            client_id=client_id,
            fhir_base_url=fhir_base_url
        )
        
        if client_instance and state:
            print("\n5. OAuth flow initiated successfully!")
            print("Follow the instructions above to complete authentication.")
            print("After authentication, you can use the client to access patient data.")
            
            # Example of how to continue after getting authorization code
            print("\n6. Example of completing the flow:")
            print("After user authorization, you would:")
            print("   auth_code = 'authorization_code_from_callback'")
            print("   token_response = client.exchange_code_for_token(auth_code)")
            print("   patient_data = client.get_patient_data()")
            print("   insights = client.get_clinical_insights()")
        
    except Exception as e:
        print(f"✗ Error during EPIC integration setup: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your EPIC client ID is correct")
        print("2. Check that your FHIR base URL is valid")
        print("3. Ensure you have internet connectivity")
        print("4. Verify EPIC FHIR service is available")


def demo_mode():
    """Run demo mode with sample patient data."""
    print("\n=== DEMO MODE ===")
    print("Simulating EPIC FHIR integration with sample data...\n")
    
    # Sample patient data that would come from EPIC FHIR
    sample_patient_data = {
        'patient': {
            'id': 'epic-patient-123',
            'name': [{'given': ['John'], 'family': 'Smith'}],
            'birthDate': '1975-03-15',
            'gender': 'male'
        },
        'conditions': [
            {
                'code': {
                    'text': 'Type 2 Diabetes Mellitus',
                    'coding': [{'display': 'Type 2 Diabetes Mellitus'}]
                }
            },
            {
                'code': {
                    'text': 'Hypertension',
                    'coding': [{'display': 'Essential Hypertension'}]
                }
            }
        ],
        'medications': [
            {
                'medicationCodeableConcept': {
                    'text': 'Metformin 500mg',
                    'coding': [{'display': 'Metformin 500mg tablets'}]
                },
                'dosageInstruction': [{'text': 'Take twice daily with meals'}]
            },
            {
                'medicationCodeableConcept': {
                    'text': 'Lisinopril 10mg',
                    'coding': [{'display': 'Lisinopril 10mg tablets'}]
                },
                'dosageInstruction': [{'text': 'Take once daily'}]
            }
        ],
        'allergies': [
            {
                'code': {
                    'text': 'Penicillin',
                    'coding': [{'display': 'Penicillin allergy'}]
                },
                'reaction': [{'manifestation': [{'text': 'Rash, difficulty breathing'}]}]
            }
        ],
        'observations': [
            {
                'code': {
                    'text': 'Hemoglobin A1c',
                    'coding': [{'display': 'Hemoglobin A1c'}]
                },
                'valueQuantity': {'value': 7.2, 'unit': '%'}
            },
            {
                'code': {
                    'text': 'Blood Pressure',
                    'coding': [{'display': 'Blood Pressure'}]
                },
                'valueString': '140/90 mmHg'
            }
        ],
        'procedures': [
            {
                'code': {
                    'text': 'Appendectomy',
                    'coding': [{'display': 'Laparoscopic appendectomy'}]
                },
                'performedDateTime': '2020-05-15'
            }
        ]
    }
    
    # Simulate the EpicFHIRClient text conversion
    print("Sample patient data from EPIC FHIR:")
    print("=" * 50)
    
    # Create a mock client for text conversion
    try:
        from clinical_insight_bot import ClinicalInsightBot
        client = EpicFHIRClient(client_id="demo", fhir_base_url="demo")
        
        # Convert FHIR data to text
        patient_text = client.convert_fhir_to_text(sample_patient_data)
        print(patient_text)
        
        print("\n" + "=" * 50)
        print("Generating clinical insights...")
        
        # Process with Clinical Insight Bot
        insights = client.insight_bot.process_emr_text(patient_text)
        
        print("\nClinical Insights for Anesthesia Planning:")
        print("-" * 40)
        print(json.dumps(insights, indent=2))
        
    except ImportError:
        print("Clinical Insight Bot not available in demo mode")
        print("Raw patient text would be:")
        print(sample_patient_data)
    
    print("\n" + "=" * 50)
    print("Demo completed! This shows how EPIC FHIR data would be processed.")
    print("To use with real data, set up your EPIC credentials and run again.")


def test_epic_endpoints():
    """Test various EPIC FHIR endpoints."""
    print("\n=== Testing EPIC FHIR Endpoints ===")
    
    endpoints_to_test = [
        "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/",
        "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/.well-known/smart-configuration"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        try:
            import requests
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✓ Endpoint accessible (Status: {response.status_code})")
            else:
                print(f"⚠ Endpoint returned status: {response.status_code}")
        except Exception as e:
            print(f"✗ Endpoint test failed: {e}")


if __name__ == "__main__":
    main()
    
    # Also test endpoints
    test_epic_endpoints() 