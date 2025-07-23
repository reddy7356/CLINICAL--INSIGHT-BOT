# Cerner FHIR Integration Guide for Clinical Insight Bot

This guide walks you through connecting the Clinical Insight Bot to Cerner's health system using SMART on FHIR APIs to automatically extract patient data for anesthesia planning.

## Overview

Cerner (now Oracle Health) provides FHIR R4 APIs that allow third-party applications to access patient data through the SMART on FHIR framework. This integration enables:

- **Automated Data Extraction**: Pull patient data directly from Cerner EHR
- **Real-time Insights**: Process current patient information for anesthesia planning  
- **Standardized Access**: Use industry-standard FHIR APIs
- **Secure Authentication**: OAuth 2.0 with SMART on FHIR

## Prerequisites

### 1. Cerner Developer Account
- Sign up for a free **CernerCare account** at [code.cerner.com](https://code.cerner.com)
- Register your application in the Cerner Code Console
- Obtain your OAuth client ID (and secret if confidential client)

### 2. Application Registration
When registering your app, you'll need:
- **Application Name**: "Clinical Insight Bot" or your preferred name
- **Application Type**: Patient-facing or Provider-facing
- **FHIR Specification**: R4
- **Redirect URI**: `http://localhost:8080/callback` (for testing)
- **Launch URL**: Your application's launch endpoint
- **Scopes**: Patient data access scopes

### 3. Python Dependencies
```bash
pip install requests
```

## Setup Instructions

### Step 1: Configure Environment Variables

```bash
# Set your Cerner credentials
export CERNER_CLIENT_ID="your-client-id-from-cerner"
export CERNER_CLIENT_SECRET="your-client-secret"  # If confidential client
export CERNER_FHIR_URL="https://fhir-ehr-code.cerner.com/r4/your-tenant-id"
```

### Step 2: Basic Integration Example

```python
from cerner_integration import CernerFHIRClient, start_oauth_flow
import os
import json

# Initialize with your credentials
client_id = os.getenv('CERNER_CLIENT_ID')
fhir_url = os.getenv('CERNER_FHIR_URL')

# Start OAuth flow
client, state = start_oauth_flow(client_id, fhir_url)

# After user authorization, exchange code for token
authorization_code = "code-from-oauth-callback"
token_response = client.exchange_code_for_token(authorization_code)

# Get clinical insights for a patient
insights = client.get_clinical_insights(patient_id="12345")
print(json.dumps(insights, indent=2))
```

## FHIR Scopes and Permissions

### Required Scopes
The integration requests the following FHIR scopes:

```python
scopes = [
    'patient/Patient.read',           # Patient demographics
    'patient/Observation.read',       # Lab values, vitals
    'patient/Condition.read',         # Diagnoses, comorbidities
    'patient/MedicationRequest.read', # Current medications
    'patient/AllergyIntolerance.read',# Allergies
    'patient/Procedure.read',         # Surgical history
    'patient/DiagnosticReport.read',  # Lab reports
    'patient/DocumentReference.read', # Clinical documents
    'openid',                        # OpenID Connect
    'fhirUser',                      # FHIR user resource
    'online_access'                  # Refresh tokens
]
```

### Scope Meanings
- **`patient/*`**: Access to specific patient resources in context
- **`user/*`**: Access to resources the authenticated user can see
- **`system/*`**: Server-to-server access (backend services)

## Authentication Flow

### 1. Patient-Facing Apps (Standalone Launch)
```python
# Initialize client
client = CernerFHIRClient(
    client_id="your-client-id",
    fhir_base_url="https://fhir-ehr-code.cerner.com/r4/tenant-id"
)

# Get authorization URL
auth_url, state = client.get_authorization_url()

# User visits auth_url and authorizes app
# Callback receives authorization code
# Exchange code for token
token_response = client.exchange_code_for_token(auth_code)
```

### 2. Provider-Facing Apps (EHR Launch)
```python
# For EHR-launched apps with launch context
launch_context = "launch-id-from-ehr"
auth_url, state = client.get_authorization_url(launch_context=launch_context)
```

## Data Extraction and Processing

### Retrieved FHIR Resources
The integration automatically extracts:

1. **Patient Demographics**
   - Name, age, gender, birth date
   - Contact information

2. **Observations** 
   - Laboratory values (Hgb, platelets, creatinine, etc.)
   - Vital signs (BP, HR, O2 sat)
   - Clinical measurements

3. **Conditions**
   - Active diagnoses
   - Past medical history
   - Comorbidities relevant to anesthesia

4. **Medications**
   - Active prescriptions
   - Medication history
   - Dosages and frequencies

5. **Allergies**
   - Drug allergies
   - Environmental allergies
   - Reaction descriptions

6. **Procedures**
   - Surgical history
   - Procedure dates and descriptions

### FHIR to Text Conversion
The integration converts FHIR resources to structured text:

```python
patient_data = client.get_patient_data("patient-123")
patient_text = client.convert_fhir_to_text(patient_data)

# Example output:
"""
PATIENT: Jane Smith
AGE: 68 years old
GENDER: Female

PAST MEDICAL HISTORY:
- Hypertension
- Type 2 Diabetes Mellitus
- Chronic kidney disease

MEDICATIONS:
- Metoprolol 50mg BID
- Insulin glargine 24 units nightly
- Lisinopril 10mg daily

ALLERGIES:
- Penicillin (rash)
- Morphine (nausea)

LABORATORY VALUES:
Hemoglobin: 11.8 g/dL
Creatinine: 1.4 mg/dL
Platelets: 245 K/uL
"""
```

## Security and Compliance

### HIPAA Compliance
- **Encryption**: All API calls use HTTPS/TLS 1.2+
- **Authentication**: OAuth 2.0 with SMART on FHIR
- **Access Controls**: Scope-limited access to patient data
- **Audit Trails**: Requests are logged by Cerner

### Best Practices
1. **Store Tokens Securely**: Never log or expose access tokens
2. **Token Refresh**: Handle token expiration gracefully
3. **Error Handling**: Implement robust error handling for API failures
4. **Rate Limiting**: Respect Cerner's API rate limits
5. **Data Minimization**: Only request needed scopes and data

## Testing and Development

### Cerner Sandbox Environment
- **Code Environment**: https://fhir-ehr-code.cerner.com/r4/
- **Test Patient Data**: Use Cerner's sample patients
- **No PHI**: Sandbox contains synthetic data only

### Test Patient IDs
Cerner provides test patients for development:
- `12724066`: Adult patient with comprehensive data
- `12724067`: Pediatric patient
- `12724068`: Patient with multiple conditions

### Validation Checklist
- [ ] OAuth flow completes successfully
- [ ] FHIR resources are retrieved without errors
- [ ] Patient data converts to text format correctly
- [ ] Clinical Insight Bot processes the text
- [ ] Output includes anesthesia-relevant information
- [ ] Error handling works for various scenarios

## Production Deployment

### Environment Configuration
```bash
# Production environment variables
export CERNER_CLIENT_ID="prod-client-id"
export CERNER_CLIENT_SECRET="prod-client-secret"
export CERNER_FHIR_URL="https://fhir-ehr.cerner.com/r4/tenant-id"
export ENCRYPTION_KEY="your-encryption-key-for-tokens"
```

## Support and Resources

### Cerner Documentation
- [FHIR API Documentation](https://fhir.cerner.com/)
- [SMART on FHIR Specification](https://hl7.org/fhir/smart-app-launch/)
- [OAuth 2.0 Guide](https://tools.ietf.org/html/rfc6749)

### Community Support
- [Cerner FHIR Developers Google Group](https://groups.google.com/forum/#!forum/cerner-fhir-developers)
- [SMART on FHIR Community](https://chat.fhir.org/#narrow/stream/179170-smart)

---

**⚠️ Important Security Note**: This integration handles protected health information (PHI). Ensure your implementation complies with HIPAA, institutional policies, and applicable regulations. Always test thoroughly in sandbox environments before production deployment. 