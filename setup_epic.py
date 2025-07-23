#!/usr/bin/env python3
"""
EPIC FHIR Integration Setup Script
Helps configure and test EPIC FHIR connection for Clinical Insight Bot.
"""

import os
import sys
import requests
from typing import Dict, Any


def test_epic_connection(fhir_url: str = None) -> bool:
    """Test connection to EPIC FHIR server."""
    if not fhir_url:
        fhir_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
    
    print(f"Testing connection to: {fhir_url}")
    
    try:
        # Test the well-known configuration endpoint
        well_known_url = f"{fhir_url.rstrip('/')}/.well-known/smart-configuration"
        response = requests.get(well_known_url, timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            print("✓ Successfully connected to EPIC FHIR server")
            print(f"  Authorization endpoint: {config.get('authorization_endpoint', 'Not found')}")
            print(f"  Token endpoint: {config.get('token_endpoint', 'Not found')}")
            return True
        else:
            print(f"✗ Connection failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def setup_environment_variables():
    """Help user set up environment variables for EPIC integration."""
    print("\n=== EPIC Environment Setup ===")
    print("Setting up environment variables for EPIC FHIR integration...\n")
    
    # Get current values
    current_client_id = os.getenv('EPIC_CLIENT_ID', '')
    current_client_secret = os.getenv('EPIC_CLIENT_SECRET', '')
    current_fhir_url = os.getenv('EPIC_FHIR_URL', 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/')
    
    print("Current configuration:")
    print(f"  EPIC_CLIENT_ID: {'Set' if current_client_id else 'Not set'}")
    print(f"  EPIC_CLIENT_SECRET: {'Set' if current_client_secret else 'Not set'}")
    print(f"  EPIC_FHIR_URL: {current_fhir_url}")
    
    # Ask for new values
    print("\nEnter new values (press Enter to keep current):")
    
    client_id = input(f"EPIC Client ID [{current_client_id[:8] + '...' if current_client_id else 'None'}]: ").strip()
    if not client_id:
        client_id = current_client_id
    
    client_secret = input(f"EPIC Client Secret [{'Set' if current_client_secret else 'None'}]: ").strip()
    if not client_secret:
        client_secret = current_client_secret
    
    fhir_url = input(f"EPIC FHIR URL [{current_fhir_url}]: ").strip()
    if not fhir_url:
        fhir_url = current_fhir_url
    
    # Validate required fields
    if not client_id:
        print("✗ Client ID is required!")
        return False
    
    # Create export commands
    export_commands = [
        f"export EPIC_CLIENT_ID='{client_id}'",
        f"export EPIC_FHIR_URL='{fhir_url}'"
    ]
    
    if client_secret:
        export_commands.append(f"export EPIC_CLIENT_SECRET='{client_secret}'")
    
    print("\n" + "="*50)
    print("Environment Variable Setup Commands:")
    print("="*50)
    
    for cmd in export_commands:
        print(cmd)
    
    print("\nTo make these permanent, add them to your shell profile:")
    print("  ~/.bashrc (for bash)")
    print("  ~/.zshrc (for zsh)")
    print("  ~/.profile (for general shell)")
    
    # Ask to apply to current session
    apply = input("\nApply to current session? (y/n): ").lower()
    if apply == 'y':
        os.environ['EPIC_CLIENT_ID'] = client_id
        os.environ['EPIC_FHIR_URL'] = fhir_url
        if client_secret:
            os.environ['EPIC_CLIENT_SECRET'] = client_secret
        print("✓ Environment variables set for current session")
        return True
    
    return True


def check_epic_app_registration():
    """Guide user through EPIC app registration process."""
    print("\n=== EPIC App Registration Guide ===")
    print("To use EPIC FHIR APIs, you need to register your application.\n")
    
    print("1. Visit the EPIC on FHIR website:")
    print("   https://fhir.epic.com/\n")
    
    print("2. Click 'Build Apps' and then 'Get Started'")
    print("   - Create an account if you don't have one")
    print("   - Log in to the Developer Portal\n")
    
    print("3. Create a new application:")
    print("   - Application Name: 'Clinical Insight Bot'")
    print("   - Application Type: 'Confidential Client' (recommended)")
    print("   - Redirect URI: 'http://localhost:8080/callback'")
    print("   - FHIR Version: 'R4'\n")
    
    print("4. Select required scopes:")
    print("   ☑ patient/Patient.read")
    print("   ☑ patient/Observation.read")
    print("   ☑ patient/Condition.read")
    print("   ☑ patient/MedicationRequest.read")
    print("   ☑ patient/AllergyIntolerance.read")
    print("   ☑ patient/Procedure.read")
    print("   ☑ patient/DiagnosticReport.read")
    print("   ☑ openid")
    print("   ☑ fhirUser\n")
    
    print("5. After registration, you'll receive:")
    print("   - Client ID (public)")
    print("   - Client Secret (keep secure)")
    print("   - FHIR Base URL")
    
    print("\n6. For testing, EPIC provides a sandbox environment:")
    print("   - You can test with synthetic patient data")
    print("   - No real patient data is accessed")
    print("   - Use MyChart credentials for testing")
    
    input("\nPress Enter when you have completed app registration...")


def test_oauth_flow():
    """Test the OAuth flow with user's credentials."""
    print("\n=== Testing OAuth Flow ===")
    
    client_id = os.getenv('EPIC_CLIENT_ID')
    if not client_id:
        print("✗ EPIC_CLIENT_ID not set. Please run environment setup first.")
        return False
    
    try:
        from epic_integration import start_epic_oauth_flow
        
        print(f"Testing OAuth flow with Client ID: {client_id}")
        client, state = start_epic_oauth_flow(client_id)
        
        if client and state:
            print("✓ OAuth flow setup successful!")
            print("✓ Authorization URL generated")
            print("✓ Ready for user authentication")
            return True
        else:
            print("✗ OAuth flow setup failed")
            return False
            
    except Exception as e:
        print(f"✗ OAuth test failed: {e}")
        return False


def run_full_test():
    """Run a complete test of the EPIC integration."""
    print("\n=== Full EPIC Integration Test ===")
    
    # Test 1: Connection
    print("\n1. Testing EPIC FHIR server connection...")
    fhir_url = os.getenv('EPIC_FHIR_URL', 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/')
    if not test_epic_connection(fhir_url):
        print("✗ Connection test failed")
        return False
    
    # Test 2: Environment variables
    print("\n2. Checking environment variables...")
    client_id = os.getenv('EPIC_CLIENT_ID')
    if not client_id:
        print("✗ EPIC_CLIENT_ID not set")
        return False
    print("✓ Environment variables configured")
    
    # Test 3: OAuth flow setup
    print("\n3. Testing OAuth flow setup...")
    if not test_oauth_flow():
        return False
    
    # Test 4: Import test
    print("\n4. Testing module imports...")
    try:
        from epic_integration import EpicFHIRClient
        from clinical_insight_bot import ClinicalInsightBot
        print("✓ All modules imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED!")
    print("✓ EPIC FHIR integration is ready to use")
    print("✓ Run 'python epic_example.py' to see it in action")
    print("="*50)
    
    return True


def main():
    """Main setup workflow."""
    print("EPIC FHIR Integration Setup")
    print("="*40)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Test EPIC FHIR connection")
        print("2. Set up environment variables")
        print("3. EPIC app registration guide")
        print("4. Test OAuth flow")
        print("5. Run full integration test")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            fhir_url = input("FHIR URL (or Enter for default): ").strip()
            if not fhir_url:
                fhir_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
            test_epic_connection(fhir_url)
            
        elif choice == '2':
            setup_environment_variables()
            
        elif choice == '3':
            check_epic_app_registration()
            
        elif choice == '4':
            test_oauth_flow()
            
        elif choice == '5':
            run_full_test()
            
        elif choice == '6':
            print("Exiting setup...")
            break
            
        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main() 