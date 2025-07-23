#!/usr/bin/env python3
"""
Setup script for Cerner FHIR integration
Helps configure environment variables and test the connection
"""

import os
import subprocess

def setup_environment():
    """Interactive setup for Cerner environment variables."""
    
    print("🏥 Clinical Insight Bot - Cerner Setup")
    print("=" * 50)
    
    # Get client ID
    client_id = input("\nEnter your Cerner Client ID: ").strip()
    
    # Ask about client secret (optional for public clients)
    has_secret = input("\nDo you have a client secret? (y/n): ").lower() == 'y'
    client_secret = ""
    if has_secret:
        client_secret = input("Enter your client secret: ").strip()
    
    # FHIR URL selection
    print("\nSelect FHIR environment:")
    print("1. Sandbox (for testing) - https://fhir-ehr-code.cerner.com/r4/...")
    print("2. Production - https://fhir-ehr.cerner.com/r4/...")
    print("3. Custom URL")
    
    env_choice = input("Choose (1-3): ").strip()
    
    if env_choice == "1":
        # Default sandbox tenant
        fhir_url = "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    elif env_choice == "2":
        tenant_id = input("Enter your production tenant ID: ").strip()
        fhir_url = f"https://fhir-ehr.cerner.com/r4/{tenant_id}"
    else:
        fhir_url = input("Enter custom FHIR URL: ").strip()
    
    # Create environment setup
    env_vars = f"""
# Cerner FHIR Configuration
export CERNER_CLIENT_ID="{client_id}"
"""
    if client_secret:
        env_vars += f'export CERNER_CLIENT_SECRET="{client_secret}"\n'
    
    env_vars += f'export CERNER_FHIR_URL="{fhir_url}"\n'
    
    # Save to .env file
    with open('.env', 'w') as f:
        f.write(env_vars)
    
    print("\n✅ Configuration saved to .env file")
    print("\nTo use these settings, run:")
    print("source .env")
    
    # Also set for current session
    os.environ['CERNER_CLIENT_ID'] = client_id
    if client_secret:
        os.environ['CERNER_CLIENT_SECRET'] = client_secret
    os.environ['CERNER_FHIR_URL'] = fhir_url
    
    return client_id, client_secret, fhir_url

def test_connection():
    """Test the Cerner FHIR connection."""
    
    print("\n🔍 Testing Cerner Connection...")
    
    try:
        from cerner_integration import CernerFHIRClient
        
        client_id = os.getenv('CERNER_CLIENT_ID')
        client_secret = os.getenv('CERNER_CLIENT_SECRET')
        fhir_url = os.getenv('CERNER_FHIR_URL')
        
        if not client_id or not fhir_url:
            print("❌ Environment variables not set. Run setup first.")
            return False
        
        client = CernerFHIRClient(
            client_id=client_id,
            client_secret=client_secret,
            fhir_base_url=fhir_url
        )
        
        # Test SMART configuration discovery
        smart_config = client.discover_smart_configuration()
        print("✅ SMART configuration discovered successfully")
        print(f"   Authorization endpoint: {smart_config.get('authorization_endpoint')}")
        print(f"   Token endpoint: {smart_config.get('token_endpoint')}")
        
        # Generate test authorization URL
        auth_url, state = client.get_authorization_url()
        print("✅ OAuth authorization URL generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Setup environment variables")
    print("2. Test connection")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        setup_environment()
    
    if choice in ["2", "3"]:
        test_connection() 