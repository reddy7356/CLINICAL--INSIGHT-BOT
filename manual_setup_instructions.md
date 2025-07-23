# Manual Cerner Setup Instructions

## Step 1: Set Environment Variables

Replace `YOUR_CLIENT_ID` with your actual client ID from Cerner console:

```bash
# For sandbox testing (recommended to start)
export CERNER_CLIENT_ID="YOUR_CLIENT_ID"
export CERNER_FHIR_URL="https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"

# If you have a client secret (optional for public clients):
export CERNER_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

## Step 2: Test the Connection

```bash
python3 -c "
import os
from cerner_integration import CernerFHIRClient

client = CernerFHIRClient(
    client_id=os.getenv('CERNER_CLIENT_ID'),
    client_secret=os.getenv('CERNER_CLIENT_SECRET'),
    fhir_base_url=os.getenv('CERNER_FHIR_URL')
)

try:
    smart_config = client.discover_smart_configuration()
    print('✅ Connection successful!')
    print(f'Authorization endpoint: {smart_config.get(\"authorization_endpoint\")}')
    
    auth_url, state = client.get_authorization_url()
    print(f'✅ OAuth URL generated: {auth_url[:50]}...')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## Step 3: Run Example

```bash
python3 cerner_example.py
```

## Quick Commands

1. Set your client ID:
```bash
export CERNER_CLIENT_ID="your-actual-client-id"
```

2. Set sandbox FHIR URL:
```bash
export CERNER_FHIR_URL="https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
```

3. Test connection:
```bash
python3 cerner_example.py
``` 