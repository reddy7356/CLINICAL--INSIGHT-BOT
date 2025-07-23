#!/usr/bin/env python3
"""
Epic OAuth Troubleshooting Test
Simple test to diagnose OAuth issues with Epic FHIR
"""

import os
import urllib.parse
from epic_integration import EpicFHIRClient

def test_epic_oauth():
    """Test Epic OAuth setup step by step"""
    
    print("=== Epic OAuth Troubleshooting ===\n")
    
    # Get credentials
    client_id = os.getenv('EPIC_CLIENT_ID')
    fhir_url = os.getenv('EPIC_FHIR_URL')
    
    print(f"1. Client ID: {client_id}")
    print(f"2. FHIR URL: {fhir_url}")
    
    if not client_id:
        print("❌ EPIC_CLIENT_ID not set!")
        return
    
    # Create client
    client = EpicFHIRClient(
        client_id=client_id,
        fhir_base_url=fhir_url,
        redirect_uri="http://localhost:8080/callback"  # Standard redirect
    )
    
    try:
        print("\n3. Testing SMART configuration discovery...")
        smart_config = client.discover_smart_configuration()
        print("✅ SMART config discovered successfully")
        print(f"   Auth endpoint: {smart_config.get('authorization_endpoint')}")
        print(f"   Token endpoint: {smart_config.get('token_endpoint')}")
        
        print("\n4. Generating OAuth URL...")
        
        # Use simpler scopes to avoid issues
        simple_scopes = [
            'patient/Patient.read',
            'patient/Observation.read',
            'patient/Condition.read',
            'openid',
            'fhirUser'
        ]
        
        auth_url, state = client.get_authorization_url(scopes=simple_scopes)
        
        print("✅ OAuth URL generated successfully")
        print(f"\n5. Authorization URL:")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        
        # Parse URL to check parameters
        parsed = urllib.parse.urlparse(auth_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        print(f"\n6. URL Parameters Check:")
        print(f"   client_id: {params.get('client_id', ['Missing'])[0]}")
        print(f"   response_type: {params.get('response_type', ['Missing'])[0]}")
        print(f"   redirect_uri: {params.get('redirect_uri', ['Missing'])[0]}")
        print(f"   scope: {params.get('scope', ['Missing'])[0]}")
        print(f"   state: {params.get('state', ['Missing'])[0][:20]}...")
        print(f"   aud: {params.get('aud', ['Missing'])[0]}")
        
        print(f"\n7. Try this simplified URL in your browser:")
        print("   (Copy and paste this URL)")
        
        # Create a simpler URL for testing
        simple_params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8080/callback',
            'scope': 'patient/Patient.read openid fhirUser',
            'state': 'test123',
            'aud': fhir_url
        }
        
        simple_url = f"{smart_config['authorization_endpoint']}?" + urllib.parse.urlencode(simple_params)
        print(simple_url)
        
        print(f"\n8. Alternative redirect URIs to try:")
        print("   - https://fhir.epic.com/test/smart")
        print("   - http://localhost:8080/callback")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_correct_redirect():
    """Test with Epic's standard redirect URI"""
    
    print("\n=== Testing with Epic Standard Redirect ===")
    
    client_id = os.getenv('EPIC_CLIENT_ID')
    fhir_url = os.getenv('EPIC_FHIR_URL')
    
    # Use Epic's standard test redirect
    client = EpicFHIRClient(
        client_id=client_id,
        fhir_base_url=fhir_url,
        redirect_uri="https://fhir.epic.com/test/smart"  # Epic's test redirect
    )
    
    try:
        smart_config = client.discover_smart_configuration()
        
        # Minimal scopes
        minimal_scopes = ['patient/Patient.read', 'openid']
        
        auth_url, state = client.get_authorization_url(scopes=minimal_scopes)
        
        print("✅ URL with Epic's standard redirect:")
        print(auth_url)
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Error with standard redirect: {e}")
        return None

if __name__ == "__main__":
    test_epic_oauth()
    test_with_correct_redirect() 